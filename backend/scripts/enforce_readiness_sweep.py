"""Enforce-readiness sweep (Permitted / enforce decision).

Runs the ensembled judge on a representative random sample of real recommendations and
reports the needs-review rate under the CURRENT disagreement guard vs a REFINED guard
(flag only genuine REJECT-vs-non-REJECT splits). Drives the enforce-flip decision and
the guard-recalibration conversation with Luda. See enforce_readiness_findings.md.

Run in the prod container:
  docker exec -i ai-pathway-backend-1 python - < backend/scripts/enforce_readiness_sweep.py
Read-only (no writes). Sample size / seed via env: SWEEP_N (default 12), SWEEP_SEED (7).
"""
import asyncio
import os
import random
import sys
from statistics import median

sys.path.insert(0, "/app")
import logging  # noqa: E402
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

from sqlalchemy import select  # noqa: E402
from app.database import AsyncSessionLocal  # noqa: E402
from app.models.goal import Goal  # noqa: E402
from app.services.recommendation_judge import _judge_once  # noqa: E402
from app.services.judge_scoring import verdict_from_scores  # noqa: E402
from app.services.ontology import get_ontology_service  # noqa: E402

N = int(os.environ.get("SWEEP_N", "12"))
SEED = int(os.environ.get("SWEEP_SEED", "7"))
K = 5
KEYS = ("jd_coverage", "role_fit_strength", "ontology_precision", "gap_validity")


def _li(fr):
    pa = (fr or {}).get("profile_analysis", {}) or {}
    cur = pa.get("top_10_current_skills", []) or []
    return ((pa.get("profile_summary", "") or "") + "\nCurrent: "
            + ", ".join(s.get("skill_name", "") for s in cur[:8])).strip()


async def main() -> int:
    onto = get_ontology_service()
    md = onto.format_skills_for_prompt()
    valid = onto.get_all_skill_ids()
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(Goal).where(Goal.full_result.isnot(None)))
        goals = [g for g in r.scalars().all()
                 if g.target_jd_text and (g.full_result or {}).get("top_10_target_skills")]
    random.seed(SEED)
    random.shuffle(goals)
    picked = goals[:N]

    cur_rev = ref_rev = 0
    bases = {"ACCEPT": 0, "ACCEPT_WITH_REVIEW": 0, "REJECT": 0}
    for g in picked:
        skills = g.full_result["top_10_target_skills"][:5]
        pairs = await asyncio.gather(
            *[_judge_once(g.target_jd_text, _li(g.full_result), skills, md, valid) for _ in range(K)])
        results = [p[0] for p in pairs]
        med = {k: round(median(r2["scores"][k] for r2 in results), 4) for k in KEYS}
        _comp, _gf, base = verdict_from_scores(med)
        bases[base] = bases.get(base, 0) + 1
        rv = [r2["overall_verdict"] for r2 in results]
        unanimous = len(set(rv)) == 1
        cur_v = base if (unanimous or base == "ACCEPT_WITH_REVIEW") else (
            "ACCEPT_WITH_REVIEW" if base in ("ACCEPT", "REJECT") else base)
        genuine = any(v == "REJECT" for v in rv) and any(v != "REJECT" for v in rv)
        ref_v = base if base == "REJECT" else (
            "ACCEPT_WITH_REVIEW" if (base == "ACCEPT_WITH_REVIEW" or genuine) else "ACCEPT")
        cur_rev += cur_v != "ACCEPT"
        ref_rev += ref_v != "ACCEPT"

    n = len(picked)
    print(f"Enforce-readiness sweep: N={n} (seed={SEED}), K={K}")
    print("median base verdicts:", bases)
    print(f"needs_review CURRENT guard: {cur_rev}/{n} ({round(cur_rev / n * 100)}%)" if n else "no recs")
    print(f"needs_review REFINED guard: {ref_rev}/{n} ({round(ref_rev / n * 100)}%)" if n else "")
    print("If the two rates match and base-REJECT is high, the blocker is judge/recommender "
          "calibration, NOT the guard - see enforce_readiness_findings.md.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
