"""Shadow-gate verdict sweep (Trust Before Intelligence - Governance validation).

Replays the recommendation judge gate across recent real production recommendations
(Goal.full_result) using the DEPLOYED code + the pinned calibrated judge (gpt-4.1),
exactly as the live shadow gate in analysis.py would. Use this to validate the gate's
verdict distribution BEFORE promoting it from shadow mode to hard-gating.

Run inside the prod backend container:
    docker exec -i ai-pathway-backend-1 python - < backend/scripts/shadow_verdict_sweep.py
or locally against the dev DB:
    cd backend && py -3.12 scripts/shadow_verdict_sweep.py

Read-only: never writes to the DB. Idempotent (same DB -> same sample; gpt-4.1 at
temperature 0.0 is reproducible).
"""
import asyncio
import logging
import sys
from collections import Counter

sys.path.insert(0, "/app")
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

from sqlalchemy import select  # noqa: E402
from app.database import AsyncSessionLocal  # noqa: E402
from app.models.goal import Goal  # noqa: E402
from app.services.recommendation_judge import evaluate_recommendation, gate_decision  # noqa: E402

N = 12  # distinct recent recommendations to judge


def _li_text(full_result: dict) -> str:
    pa = (full_result or {}).get("profile_analysis", {}) or {}
    summary = pa.get("profile_summary", "") or ""
    current = pa.get("top_10_current_skills", []) or []
    names = ", ".join(s.get("skill_name", "") for s in current[:8])
    return (summary + ("\nCurrent skills: " + names if names else "")).strip()


async def _judge_one(goal: Goal) -> dict | None:
    fr = goal.full_result or {}
    skills = (fr.get("top_10_target_skills") or fr.get("top_10_skill_gaps") or [])[:5]
    if not goal.target_jd_text or not skills:
        return None
    res = await evaluate_recommendation(
        jd_text=goal.target_jd_text, li_text=_li_text(fr), skills=skills
    )
    d = gate_decision(res)
    return {
        "role": (goal.target_role or "?")[:34],
        "n": len(skills),
        "composite": d["composite"],
        "verdict": d["verdict"],
        "action": d["action"],
        "fails": ",".join(d["gate_failures"]) or "-",
        "scores": res.get("scores", {}),
    }


async def main() -> None:
    async with AsyncSessionLocal() as db:
        r = await db.execute(
            select(Goal).where(Goal.full_result.isnot(None)).order_by(Goal.created_at.desc())
        )
        goals = r.scalars().all()

    picked, seen = [], set()
    for g in goals:
        key = (g.target_role or "")[:40]
        if key in seen:
            continue
        seen.add(key)
        picked.append(g)
        if len(picked) >= N:
            break

    print(f"Replaying shadow gate on {len(picked)} distinct recent recommendations (judge=gpt-4.1)\n")
    rows = []
    for g in picked:
        try:
            row = await _judge_one(g)
            if row:
                rows.append(row)
        except Exception as e:  # noqa: BLE001 - report and continue the sweep
            print("  ERR", (g.target_role or "?")[:30], type(e).__name__, str(e)[:80])

    print(f"\n{'ROLE':36} {'#':>2} {'COMP':>5}  {'VERDICT':18} {'ACTION':10} GATES_FAILED")
    print("-" * 92)
    counts = Counter()
    for x in rows:
        counts[x["action"]] += 1
        print(f"{x['role']:36} {x['n']:>2} {x['composite']:>5.2f}  {x['verdict']:18} {x['action']:10} {x['fails']}")
    print("-" * 92)
    print("VERDICT DISTRIBUTION:", dict(counts), f"| total judged: {len(rows)}")


if __name__ == "__main__":
    asyncio.run(main())
