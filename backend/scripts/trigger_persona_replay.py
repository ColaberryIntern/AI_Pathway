"""Trigger a fresh analysis through the current engine for any persona
in the corpus, WITHOUT deleting prior Goal/LearningPath records.

The old data stays in the DB as the audit trail of what Luda originally
saw. The new Goal+Path becomes the LATEST for that profile, so the
analysis-results endpoint will serve the fresh version. This is what
flips a persona's QA dossier from RED to GREEN after engine fixes.

Run inside the backend container:
    python /app/trigger_persona_replay.py <persona_id> [<persona_id> ...]

After the replay finishes, the script prints the new Goal IDs so they
can be recorded in docs/qa_dossier/verification_runs.md as provenance.
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import urllib.request
from datetime import datetime, timezone

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def replay_one(persona_id: str) -> dict:
    from app.database import AsyncSessionLocal
    from app.models.goal import Goal
    from app.models.learning_path import LearningPath
    from app.models.profile import Profile
    from sqlalchemy import select

    # persona_corpus is at /app/persona_corpus.py inside the container
    sys.path.insert(0, "/app")
    from persona_corpus import PERSONAS  # type: ignore

    persona = next((p for p in PERSONAS if p["id"] == persona_id), None)
    if not persona:
        return {"persona_id": persona_id, "status": "unknown_persona"}

    profile_id = persona.get("profile_id")
    if not profile_id:
        return {"persona_id": persona_id, "status": "no_profile_id"}

    async with AsyncSessionLocal() as db:
        r = await db.execute(select(Profile).where(Profile.id == profile_id))
        prof = r.scalars().first()
        if not prof:
            return {"persona_id": persona_id, "status": "profile_not_in_db"}
        pd = prof.profile_data or {}
        jd = pd.get("target_jd") or pd.get("target_jd_text") or ""

        # Record the prior latest goal so we can confirm preservation
        r = await db.execute(
            select(Goal).where(Goal.profile_id == profile_id)
            .order_by(Goal.created_at.desc())
        )
        prior_goal = r.scalars().first()
        prior_goal_id = prior_goal.id if prior_goal else None

    if not jd:
        return {"persona_id": persona_id, "status": "no_stored_jd"}

    print(f"  Replaying {persona_id} ({persona['role']})")
    print(f"    profile_id: {profile_id}")
    print(f"    prior latest goal: {prior_goal_id}")
    print(f"    JD chars: {len(jd)}")

    payload = {
        "profile_id": profile_id,
        "target_jd_text": jd,
        "target_role": persona.get("role"),
        "skip_assessment": True,
        # No selected_skill_ids - let the engine pick the top 5 from its
        # rubric-reranked output. This is what Luda would see if she did
        # not customize the selection on the Top 5 page.
        # No self_assessed_skills - the orchestrator falls back to the
        # profile's estimated_current_skills (same as production default).
    }
    req = urllib.request.Request(
        "http://localhost:8080/api/analysis/full",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        _ = r.read()

    # Look up the new goal that was created
    async with AsyncSessionLocal() as db:
        r = await db.execute(
            select(Goal).where(Goal.profile_id == profile_id)
            .order_by(Goal.created_at.desc())
        )
        new_goal = r.scalars().first()
        new_goal_id = new_goal.id if new_goal else None
        new_path_id = None
        if new_goal:
            r = await db.execute(
                select(LearningPath).where(LearningPath.goal_id == new_goal.id)
            )
            lp = r.scalars().first()
            new_path_id = lp.id if lp else None

        # Activate the new path so modules + lessons exist
        if new_path_id:
            try:
                act = urllib.request.Request(
                    f"http://localhost:8080/api/learning/{new_path_id}/activate",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    data=b"{}",
                )
                with urllib.request.urlopen(act, timeout=120) as r:
                    _ = r.read()
                print(f"    activated path {new_path_id}")
            except Exception as exc:
                print(f"    activation skipped: {exc}")

    return {
        "persona_id": persona_id,
        "profile_id": profile_id,
        "prior_goal_id": prior_goal_id,
        "new_goal_id": new_goal_id,
        "new_path_id": new_path_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "replayed",
    }


async def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: trigger_persona_replay.py <persona_id> [<persona_id> ...]\n")
        return 3

    results = []
    for persona_id in sys.argv[1:]:
        print(f"\n=== {persona_id} ===")
        try:
            res = await replay_one(persona_id)
        except Exception as exc:
            res = {"persona_id": persona_id, "status": f"error: {exc}"}
        results.append(res)
        print(f"  result: {res.get('status')}")

    print()
    print("=== SUMMARY ===")
    for r in results:
        print(json.dumps(r))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
