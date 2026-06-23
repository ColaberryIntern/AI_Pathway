"""Reject diagnostic (enforce / recommender-vs-judge decision input for Luda).

For a representative random sample, finds the median-REJECT recommendations and shows
WHY each was rejected: failing gate(s), the uncovered AI requirements (what the JD needs
vs what was covered), and the weak-fit recommended skills. This lets Luda decide per
case whether it is a recommender gap (add the missing skill) or judge over-strictness
(loosen the gate/lexicon). Emits Markdown to stdout. Read-only.

Run: docker exec -i ai-pathway-backend-1 python - < backend/scripts/reject_diagnostic.py
Env: SWEEP_N (default 12), SWEEP_SEED (default 7) - match enforce_readiness_sweep.py.
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
from app.services.judge_scoring import verdict_from_scores, GATES  # noqa: E402
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


def _md_row(cells):
    return "| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |"


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

    rejects = []
    gate_fail = {"jd_coverage": 0, "role_fit_strength": 0, "ontology_precision": 0}
    for g in picked:
        skills = g.full_result["top_10_target_skills"][:5]
        pairs = await asyncio.gather(
            *[_judge_once(g.target_jd_text, _li(g.full_result), skills, md, valid) for _ in range(K)])
        results = [p[0] for p in pairs]
        raws = [p[1] for p in pairs]
        med = {k: round(median(r2["scores"][k] for r2 in results), 4) for k in KEYS}
        comp, _gf, base = verdict_from_scores(med)
        if base != "REJECT":
            continue
        failing = [k for k, gate in GATES.items() if med[k] < gate]
        for k in failing:
            gate_fail[k] = gate_fail.get(k, 0) + 1
        # representative run: composite closest to median composite
        comps = [r2["composite"] for r2 in results]
        ridx = min(range(len(comps)), key=lambda i: abs(comps[i] - median(comps)))
        p = raws[ridx]
        uncovered = [
            (row.get("tier") or "-", row.get("jd_requirement", "?"),
             row.get("ai_skill") or "-", row.get("covered_by") or "—")
            for row in (p.get("jd_coverage") or {}).get("requirement_analysis", [])
            if row.get("ai_type") in ("explicit", "implied") and row.get("coverage") != "full"
        ]
        weak = [(s.get("id"), s.get("fit_level"), (s.get("reasoning") or "")[:90])
                for s in (p.get("role_fit_strength") or {}).get("skills", [])
                if s.get("fit_level") != "role_specific"]
        rejects.append({"role": g.target_role or "?", "comp": comp, "scores": med,
                        "failing": failing, "skills": [s.get("skill_id") for s in skills],
                        "uncovered": uncovered, "weak": weak})

    out = [f"# Reject diagnostic - representative sample (N={len(picked)}, seed={SEED}, K={K})",
           "",
           f"Median-REJECT recommendations: **{len(rejects)}/{len(picked)}**. "
           f"Failing gate counts: jd_coverage={gate_fail['jd_coverage']}, "
           f"role_fit={gate_fail['role_fit_strength']}, ontology={gate_fail['ontology_precision']}.",
           "",
           "For each: is the uncovered requirement a skill the recommender SHOULD have "
           "included (recommender fix), or a stretch the judge is too strict on (judge "
           "recalibration)? That is the per-case call for Luda.", ""]
    for rj in rejects:
        out.append(f"## {rj['role']}  (composite {rj['comp']:.2f}, REJECT)")
        out.append(f"Failing gate(s): {', '.join(rj['failing'])}  |  scores: "
                   f"jd_cov {rj['scores']['jd_coverage']}, role_fit {rj['scores']['role_fit_strength']}, "
                   f"gap {rj['scores']['gap_validity']}")
        out.append(f"Recommended top-5: {', '.join(rj['skills'])}")
        if rj["uncovered"]:
            out.append("")
            out.append("Uncovered / partial AI requirements (what the JD needs vs what covered it):")
            out.append(_md_row(["tier", "JD requirement", "needs skill", "covered by"]))
            out.append(_md_row(["---", "---", "---", "---"]))
            for row in rj["uncovered"][:8]:
                out.append(_md_row(row))
        if rj["weak"]:
            out.append("")
            out.append("Weak-fit recommended skills (not role_specific):")
            out.append(_md_row(["skill", "fit", "judge reasoning"]))
            out.append(_md_row(["---", "---", "---"]))
            for row in rj["weak"][:6]:
                out.append(_md_row(row))
        out.append("")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
