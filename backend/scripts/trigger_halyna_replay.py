"""Replay Halyna's analysis with explicit user selection so we can verify
the May 19 fix produces chapters in the user's display order.

Runs INSIDE the backend container against localhost.
"""
import asyncio
import json
import logging
import urllib.request

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def main() -> None:
    from app.database import AsyncSessionLocal
    from app.models.profile import Profile
    from sqlalchemy import select

    HALYNA = "625c57e8-a727-47e2-85e5-f5fe015e793c"

    async with AsyncSessionLocal() as db:
        r = await db.execute(select(Profile).where(Profile.id == HALYNA))
        prof = r.scalars().first()
        pd = prof.profile_data or {}
        jd = pd.get("target_jd") or pd.get("target_jd_text") or ""

    print(f"JD text len: {len(jd)}")
    if not jd:
        print("ERROR: no stored JD for Halyna")
        return

    # Halyna's likely Top 5 page final selection (in display order):
    SELECTED = [
        "SK.COM.005",  # Cross-functional AI collaboration (was #1)
        "SK.GOV.001",  # AI governance fundamentals (was #5)
        "SK.PRM.020",  # Draft -> critique -> revise (was #6)
        "SK.PRM.003",  # Prompt debugging & iteration (was #7)
        "SK.EVL.001",  # Eval types (was #8)
    ]
    SELF_ASSESSED = {
        "SK.COM.005": 2,
        "SK.GOV.001": 1,
        "SK.PRM.020": 2,
        "SK.PRM.003": 2,
        "SK.EVL.001": 1,
    }

    payload = {
        "profile_id": HALYNA,
        "target_jd_text": jd,
        "target_role": "Director, Global Campaigns",
        "skip_assessment": True,
        "self_assessed_skills": SELF_ASSESSED,
        "selected_skill_ids": SELECTED,
    }
    print("Triggering /api/analysis/full ...")
    req = urllib.request.Request(
        "http://localhost:8080/api/analysis/full",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        body = r.read().decode("utf-8")
    res = json.loads(body)
    print("Analysis complete.")
    # Show the resulting chapters
    lp = res.get("learning_path") or {}
    chapters = lp.get("chapters") or []
    print(f"\nResulting path: {len(chapters)} chapters")
    for ch in chapters:
        sid = ch.get("primary_skill_id") or ch.get("skill_id")
        sname = ch.get("primary_skill_name") or ch.get("skill_name")
        print(f"  ch#{ch.get('chapter_number')} {sid} | {sname!r}")
    print()
    expected = list(SELECTED)
    actual = [ch.get("primary_skill_id") or ch.get("skill_id") for ch in chapters]
    if actual == expected:
        print("PASS: chapter order matches user selection EXACTLY")
    else:
        print("FAIL: chapter order does not match selection")
        print(f"  expected: {expected}")
        print(f"  actual:   {actual}")


if __name__ == "__main__":
    asyncio.run(main())
