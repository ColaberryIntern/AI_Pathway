# Enforce-readiness findings (2026-06-23) - for Luda

**Question:** can we flip `judge_gate_mode=enforce` (the deterministic gate actively
gates/regenerates live recommendations)?

**Answer: not yet - and the blocker is NOT what we thought.** It is not guard
sensitivity; it is that the calibrated judge rejects ~half of representative
recommendations.

## Data

### A. Recent-8 sample (skewed toward known-borderline test personas)
- Current guard (flag any non-unanimous panel): **62%** needs-review.
- Refined guard (flag only genuine REJECT-vs-non-REJECT splits): **50%**.
- So the refined guard removes the *spurious* accept-vs-review flags here.

### B. Representative random sample (seed=7, 12 recs across all 204, K=5)
- Median base verdicts: **ACCEPT 4 / ACCEPT_WITH_REVIEW 2 / REJECT 6**.
- Current guard: **75%** needs-review. Refined guard: **75%** - **no change**.

The refined guard does nothing on the representative sample because the review rate is
driven by **6/12 genuine median-REJECTs + 2 borderline-band**, not by accept-vs-review
split noise.

## The real finding
**~50% of representative production recommendations score a median REJECT against the
calibrated v4 judge.** That is a recommender-quality / calibration signal, not a gate
bug. Two possibilities to disambiguate:
1. **Recommender quality:** the rubric_scorer top-5 genuinely under-covers the JD or
   under-fits the role for many roles (a real upstream fix - improve ranking / inputs).
2. **Judge over-strictness:** the v4 judge was calibrated on a few personas (Halyna et
   al.) and the 0.70 jd_coverage / 0.70 role_fit gates may be too strict for the general
   population (recalibrate the lexicon / gate thresholds with the golden set).

It is almost certainly a mix. This is a **Strategic / Lexicon decision for Luda**, not
an autonomous tuning change.

## Recommendation
1. **Hold enforce.** It never blocks a user (regeneration + flag; 0/8 exhausted), but a
   ~75% "flagged for review" badge is not shippable.
2. **Diagnose the 50%:** sample the median-REJECT recs, record which gate fails
   (jd_coverage vs role_fit) and by how much, and judge a handful by eye vs the judge.
   That tells us recommender-fix vs judge-recalibration.
3. **Then** either improve the recommender or recalibrate the judge (golden-set anchored,
   re-run `judge_drift_check`), re-run `enforce_readiness_sweep.py`, and flip enforce when
   the representative review rate is acceptable (target ~10-20%).
4. The refined guard (flag only genuine reject-splits) is a small, defensible improvement
   to land alongside the recalibration - it removes spurious accept-vs-review flags.

Reproduce: `docker exec -i ai-pathway-backend-1 python - < backend/scripts/enforce_readiness_sweep.py`
