# Reject diagnostic - WHY the judge rejects ~50% (for Luda)

Representative sample (N=12, seed=7, K=5); ~6 median-REJECT. For each reject the judge
names, per JD requirement, the ontology skill that would cover it (`needs skill`) and
whether a recommended skill did (`covered by`). Reproduce:
`docker exec -i ai-pathway-backend-1 python - < backend/scripts/reject_diagnostic.py`.

**The rejects split cleanly into two causes - and both are fixable.**

## Cause 1 - RECOMMENDER GAP (the judge names a real skill we didn't recommend)
Over and over, the judge says a requirement needs a specific ontology skill that the
recommender left out of the top-5 (`covered by = —`):

| Role | Requirement | Judge says it needs | In top-5? |
|---|---|---|---|
| L&D Specialist | measure training effectiveness / demonstrate ROI | **SK.PRD.022 ROI measurement** | no |
| Director, Global Campaigns | define KPIs / performance frameworks | **SK.PRD.002 Workflow mapping** | no |
| Director, Global Campaigns | KPIs + reporting dashboards / ROI | **SK.PRD.022 ROI measurement** | no |

These are skills that exist in the ontology and that the judge itself flags as the right
coverage - the rubric_scorer just didn't rank them into the top-5 for marketing-leadership
/ L&D roles. **Fix (recommender):** floor ROI measurement (SK.PRD.022), workflow mapping
(SK.PRD.002), and use-case selection (SK.PRD.001) for these verticals (the same
role-essence-floor mechanism that already exists for Sr AI PMM). This is the bigger and
more clearly-correct half.

## Cause 2 - JUDGE OVER-COUNTS non-AI requirements (judge strictness)
The judge classifies plainly non-AI / tooling requirements as "implied AI" and then
counts them as uncovered, dragging jd_coverage down:

| Role | Requirement counted as uncovered "AI" | needs skill |
|---|---|---|
| AI Content Editor | "Apply SEO best practices / keyword research" | — (no AI skill) |
| AI Content Editor | "Use data analysis to identify trends" | — |
| L&D Specialist | "Experience with LMS (Workday, Litmos) and authoring tools" | — |

SEO, keyword research, and LMS-tool familiarity are not AI-skill requirements; counting
them as implied-AI-but-uncovered unfairly tanks the score. **Fix (judge):** tighten the
ai_type classification so tooling/SEO/process requirements are `none`, not `implied`
(a lexicon / prompt clarification), then re-validate against the golden set + drift check.

## Conclusion / recommendation
The ~50% reject is **not** "the recommendations are bad" - it is roughly half recommender
gap (missing skills the judge itself names) and half judge over-strictness (non-AI reqs
counted as uncovered). Recommended order:
1. **Recommender:** add the vertical role-essence floors (ROI / workflow / use-case for
   marketing + L&D). Cheapest, clearly correct, and likely recovers several rejects.
2. **Judge:** clarify ai_type so non-AI/tooling requirements don't count; re-run the
   golden + drift guards.
3. Re-run `enforce_readiness_sweep.py`; when the representative review rate is ~10-20%,
   flip enforce.

Both are bounded changes I can implement once you confirm direction - but the recommender
floor (1) touches the rubric and the judge lexicon (2) is a calibration change, so both
want your / Luda's sign-off first (Strategic per the Autonomy Model).

## Addendum (candidate-pool check): Fix 1 is INJECTION, not just a floor
Checked whether the judge-named skills are even in the recommender's candidate pool for
the reject goals:
- **L&D** pool: COM.005, EDU.001, COM.003, FND.002, GOV.022, PRD.020, CTIC.006, PRM.020,
  PRM.003, LRN.004 -> **PRD.022 / PRD.001 / PRD.002 absent**.
- **AI Content Editor** pool -> the named skills **absent**.
- **Director, Global Campaigns** (one variant) -> PRD.001 + PRD.002 **present** (here a
  floor/pin would keep them in the top-5).

A rubric FLOOR only reorders candidates - it cannot recover a skill that was never
surfaced. So for L&D / Content Editor the gap is **upstream of the rubric**: the JD
parser / candidate step does not surface measurement (ROI), workflow-mapping, or
use-case skills for these verticals. The correct Fix 1 is therefore a **vertical-essence
candidate INJECTION** (surface ROI / workflow / use-case for marketing + L&D *before*
ranking, analogous to `inject_foundational_prm_if_missing`) **plus** the floor for the
cases where the skill is already a candidate.

This is a larger recommender change (it alters candidate surfacing for whole verticals),
so it needs Luda's design direction before I build it - which vertical maps to which
essence skills. Once she confirms the mapping, I implement the injection + floor, re-run
`enforce_readiness_sweep.py`, and report the new reject rate.
