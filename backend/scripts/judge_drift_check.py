"""Judge calibration drift check (Trust Before Intelligence - Lexicon/Adaptive).

Runs the LIVE ensembled judge on an expert-anchored golden case (Luda's v4
interactive grading of Halyna) and compares the verdict + key sub-scores to the
expert reference. Reports agreement and flags drift beyond tolerance.

This is the periodic/triggered calibration guard (NOT a unit test - it makes real
LLM calls). Run it:
  - on any change to judge_model or the judge spec (the recalibration trigger),
  - on any ontology version change,
  - on a schedule (e.g. weekly) to catch silent model drift.

In the prod container:
  docker exec -i ai-pathway-backend-1 python - < backend/scripts/judge_drift_check.py
Exit code 0 = within tolerance; 1 = drift detected (alert / recalibrate).

The anchor mirrors docs/luda_jun19/halyna_golden.json; it is embedded so the
script is self-contained when piped into the container.
"""
import asyncio
import sys

sys.path.insert(0, "/app")
import logging  # noqa: E402
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

from sqlalchemy import select  # noqa: E402
from app.database import AsyncSessionLocal  # noqa: E402
from app.models.goal import Goal  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.services.recommendation_judge import evaluate_recommendation_stable, gate_decision  # noqa: E402

# Expert anchor (Luda v4 interactive run; source: docs/luda_jun19/halyna_golden.json).
ANCHOR = {
    "persona": "halyna",
    "profile_id": "625c57e8-a727-47e2-85e5-f5fe015e793c",
    "target_role_hint": "Director, Global Campaigns",
    "skills": ["SK.EVL.001", "SK.PRD.001", "SK.RSN.003", "SK.PRD.002",
               "SK.CTIC.006", "SK.PRM.020", "SK.PRM.003"],
    "expected": {"overall_verdict": "ACCEPT_WITH_REVIEW",
                 "jd_coverage": 1.0, "role_fit_strength": 0.929},
}
# Sub-score drift tolerance (absolute). Verdict mismatch is always a failure.
TOLERANCE = 0.15


async def _load_inputs():
    async with AsyncSessionLocal() as db:
        # Look up by profile_id (NOT Goal.id), newest goal first; fall back to role.
        r = await db.execute(
            select(Goal).where(Goal.profile_id == ANCHOR["profile_id"])
            .where(Goal.full_result.isnot(None)).order_by(Goal.created_at.desc())
        )
        g = r.scalars().first()
        if g is None:
            r = await db.execute(
                select(Goal).where(Goal.target_role.ilike(f"%{ANCHOR['target_role_hint']}%"))
                .where(Goal.full_result.isnot(None)).order_by(Goal.created_at.desc())
            )
            g = r.scalars().first()
    if g is None or not g.target_jd_text:
        raise RuntimeError("Could not load the anchor profile's JD from the DB")
    fr = g.full_result or {}
    pa = (fr.get("profile_analysis") or {})
    cur = pa.get("top_10_current_skills") or []
    li = ((pa.get("profile_summary", "") or "") + "\nCurrent: "
          + ", ".join(s.get("skill_name", "") for s in cur[:8])).strip()
    return g.target_jd_text, li


async def main() -> int:
    settings = get_settings()
    jd, li = await _load_inputs()
    skills = [{"skill_id": sid, "skill_name": sid} for sid in ANCHOR["skills"]]
    res = await evaluate_recommendation_stable(jd_text=jd, li_text=li, skills=skills)
    dec = gate_decision(res)
    exp = ANCHOR["expected"]

    verdict_ok = dec["verdict"] == exp["overall_verdict"]
    cov_drift = abs(res["scores"]["jd_coverage"] - exp["jd_coverage"])
    fit_drift = abs(res["scores"]["role_fit_strength"] - exp["role_fit_strength"])
    within_tol = cov_drift <= TOLERANCE and fit_drift <= TOLERANCE
    drift = (not verdict_ok) or (not within_tol)

    print("=== Judge drift check (persona=%s) ===" % ANCHOR["persona"])
    print("judge_model=%s | ensemble_k=%s | tolerance=%.2f"
          % (settings.judge_model, settings.judge_ensemble_k, TOLERANCE))
    print("verdict:   expected=%s  actual=%s  %s"
          % (exp["overall_verdict"], dec["verdict"], "OK" if verdict_ok else "MISMATCH"))
    print("jd_coverage:      expected=%.3f  actual=%.3f  drift=%.3f"
          % (exp["jd_coverage"], res["scores"]["jd_coverage"], cov_drift))
    print("role_fit_strength: expected=%.3f  actual=%.3f  drift=%.3f"
          % (exp["role_fit_strength"], res["scores"]["role_fit_strength"], fit_drift))
    print("ensemble: unanimous=%s spread=%.3f composite=%.3f"
          % (res.get("unanimous"), res.get("composite_spread", 0.0), dec["composite"]))
    print("RESULT:", "DRIFT - recalibrate" if drift else "within tolerance")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
