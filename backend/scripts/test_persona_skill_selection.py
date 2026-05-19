"""Run a persona's JD through the parser and compare the resulting top 10
skill list against the persona corpus expectations.

Used as the first verification gate when changing JD parser logic. Runs
inside the backend container.
"""
import asyncio
import json
import logging
import sys
import urllib.request

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def main() -> int:
    from app.database import AsyncSessionLocal
    from app.models.profile import Profile
    from sqlalchemy import select
    from persona_corpus import PERSONAS, evaluate_skill_set

    if len(sys.argv) < 2:
        print("Usage: python test_persona_skill_selection.py <persona_id>")
        print("Available personas:")
        for p in PERSONAS:
            print(f"  {p['id']}")
        return 2

    persona_id = sys.argv[1]
    persona = next((p for p in PERSONAS if p["id"] == persona_id), None)
    if not persona:
        print(f"Unknown persona: {persona_id}")
        return 2
    if not persona.get("profile_id"):
        print(f"Persona {persona_id} has no profile_id - skip")
        return 0

    async with AsyncSessionLocal() as db:
        r = await db.execute(select(Profile).where(Profile.id == persona["profile_id"]))
        prof = r.scalars().first()
        if not prof:
            print(f"Profile {persona['profile_id']} not in DB")
            return 1
        pd = prof.profile_data or {}
        jd = pd.get("target_jd") or pd.get("target_jd_text") or ""

    if not jd:
        print(f"No stored JD for {persona_id}")
        return 1

    # Build learner_profile for the parser
    learner_profile = {
        "name": prof.name,
        "current_role": prof.current_role,
        "industry": prof.industry,
        "experience_years": prof.experience_years,
        "ai_exposure_level": prof.ai_exposure_level,
        "technical_background": pd.get("technical_background", "")
                                 or persona.get("learner_technical_background", ""),
        "tools_used": pd.get("tools_used", []),
        "learning_intent": prof.learning_intent,
    }

    payload = {
        "jd_text": jd,
        "target_role": persona["role"],
        "learner_profile": learner_profile,
    }

    print(f"=== {persona_id} ({persona['role']}) ===")
    print(f"JD chars: {len(jd)}")
    print()
    req = urllib.request.Request(
        "http://localhost:8080/api/analysis/parse-jd-skills",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        res = json.loads(r.read().decode("utf-8"))

    skills = res.get("top_10_skills") or []
    skill_ids = [s.get("skill_id") for s in skills]

    print(f"Detected role: {res.get('target_role')!r}")
    print(f"Top 10 skill IDs the parser returned:")
    for i, s in enumerate(skills, 1):
        marker = ""
        if s.get("skill_id") in (persona.get("expected_top5_includes") or []):
            marker += " [EXPECTED-top5]"
        if s.get("skill_id") in (persona.get("expected_top10_includes") or []):
            marker += " [EXPECTED-top10]"
        if s.get("skill_id") in (persona.get("forbidden_in_top5") or []) and i <= 5:
            marker += " [FORBIDDEN]"
        print(f"  #{i} {s.get('skill_id')} | {s.get('skill_name')!r} | L{s.get('required_level')}{marker}")
    print()

    verdict = evaluate_skill_set(persona, skill_ids)
    print("--- Persona corpus verdict ---")
    print(f"  passed:          {verdict['passed']}")
    print(f"  top5 hits:       {verdict['top5_hits']}")
    print(f"  top5 misses:     {verdict['top5_misses']}")
    print(f"  forbidden hits:  {verdict['forbidden_hits']}")
    print(f"  top10 hits:      {verdict['top10_hits']}")
    print(f"  top10 misses:    {verdict['top10_misses']}")
    print()
    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
