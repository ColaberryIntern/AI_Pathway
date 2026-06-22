# Judge calibration: golden set + drift guard (Phase 2, item 9)

Two complementary guards keep the recommendation judge trustworthy over time
(Trust Before Intelligence - Lexicon / Adaptive).

## 1. Deterministic regression golden (CI, every run)

`backend/tests/test_judge_golden.py` + `backend/tests/golden/judge_golden.json`.

Frozen raw judge parameters from three expert-anchored v4 cases (halyna_set_a,
halyna_set_b, brittany_set_a) are scored by `deterministic_score`; the expected
output is the **trustworthy recomputation**, pinned. Any change to the weights, tier
weights, coverage/fit mapping, or gate thresholds that moves a golden case fails the
test and forces a deliberate decision.

Note: the `deterministic` block in the source file (`docs/luda_jun19/judge_detail_v4_jun19.json`)
was the **LLM self-report** (jd_coverage 0.5, role_fit 0.5), not a real
recomputation - the deterministic scorer recomputes 0.857 / 0.429 from the per-row
judgments. `test_deterministic_diverges_from_llm_selfreport` locks in exactly why the
deterministic layer exists: the model under-reports, so we never trust its
self-reported aggregates.

## 2. Calibration drift check (periodic / triggered, makes live LLM calls)

`backend/scripts/judge_drift_check.py`. Runs the live ensembled judge on the expert
anchor (Luda's v4 interactive grading of Halyna; mirrors
`docs/luda_jun19/halyna_golden.json`) and compares verdict + sub-scores to the
expert reference. Exit 0 = within tolerance, 1 = drift.

```
docker exec -i ai-pathway-backend-1 python - < backend/scripts/judge_drift_check.py
```

Expert anchor: skills = EVL.001, PRD.001, RSN.003, PRD.002, CTIC.006, PRM.020,
PRM.003; expected verdict = ACCEPT_WITH_REVIEW, jd_coverage = 1.0,
role_fit_strength = 0.929. Sub-score tolerance = 0.15 (absolute); a verdict mismatch
is always a failure.

### Last validated: 2026-06-22 (within tolerance)
verdict ACCEPT_WITH_REVIEW (matches expert), jd_coverage drift 0.038, role_fit drift
0.143. Notably the 5 ensemble runs split `[REVIEW, REJECT, ACCEPT, ACCEPT, REVIEW]`
and the disagreement guard resolved to ACCEPT_WITH_REVIEW - reproducing the expert
verdict that a single sample would have flipped. **Watch:** role_fit drift (0.143) is
near the 0.15 bound; the model rates role fit a little below the expert. If it crosses
0.15, recalibrate the LEXICON role_fit definition rather than loosening the tolerance.

## Recalibration trigger

Re-run the drift check, and recalibrate if it fails, whenever ANY of:
- `judge_model` changes (config.py) - a model swap is a recalibration event.
- The judge spec (`backend/app/data/judge_spec_v4.md`) or the LEXICON changes.
- `backend/app/data/ontology.json` version changes (skill ids / mappings shift).
- A scheduled cadence (e.g. weekly) to catch silent provider-side model drift.

Recalibration = adjust the LEXICON definitions (and, only with Luda's sign-off, the
weights/gates), then refresh the golden fixture and re-run both guards until the
expert anchor passes. A model-class change remains a Strategic Decision (escalate)
per the Autonomy Model.
