# Shadow gate verdict sample — 2026-06-20

First validation pull of the recommendation judge gate after it went live in shadow
mode in production (`judge_gate_enabled=true`, judge pinned to `gpt-4.1`).

**Method:** organic shadow verdicts in the prod logs = 0 (no live analysis traffic
since deploy), so the gate was replayed across 11 distinct recent real production
recommendations (`Goal.full_result`) using the deployed code + live gpt-4.1, exactly
as the live shadow path does. Reproduce with `backend/scripts/shadow_verdict_sweep.py`.

## Result

| Role | # | Composite | Verdict | Action | Gates failed |
|---|---|---|---|---|---|
| Senior Frontend Engineer | 5 | 0.84 | REJECT | regenerate | role_fit_strength |
| Director, Global Campaigns | 5 | 0.85 | ACCEPT | accept | - |
| Sr. AI Product Marketing Manager | 5 | 0.95 | ACCEPT | accept | - |
| AI Content Editor | 5 | 0.75 | REJECT | regenerate | jd_coverage |
| Learning and Development Specialist | 5 | 0.51 | REJECT | regenerate | jd_coverage, role_fit_strength |
| Sr. Product Marketing Manager | 5 | 0.93 | ACCEPT | accept | - |
| CTO | 5 | 0.96 | ACCEPT | accept | - |
| AI Operations Manager | 5 | 0.82 | ACCEPT_WITH_REVIEW | review | - |
| AI Security Engineer | 5 | 0.47 | REJECT | regenerate | jd_coverage, role_fit_strength |
| Full Stack AI Developer | 5 | 0.84 | ACCEPT_WITH_REVIEW | review | - |
| SAP Joule AI Solution Architect | 4 | 0.87 | ACCEPT | accept | - |

**Distribution:** ACCEPT 5 (45%) · ACCEPT_WITH_REVIEW 2 (18%) · REJECT 4 (36%) · total 11

## Reading

- The gate **discriminates** rather than rubber-stamps: strong recommendations (CTO 0.96,
  Sr. AI PMM 0.95, Sr. PMM 0.93) pass cleanly; weak ones (AI Security Engineer 0.47, L&D
  Specialist 0.51) fail both deterministic gates hard. This is the intended behavior.
- **36% REJECT** is the headline. REJECTs are driven by the deterministic gates
  (jd_coverage < 0.70 or role_fit_strength < 0.70), not just low composite. Two are
  unambiguous (0.47, 0.51 — both gates fail). Two are **borderline and need a human read**:
  - Senior Frontend Engineer: composite 0.84 but role_fit gate failed → REJECT. A high
    composite with a single failed gate forcing REJECT may be too harsh for a non-AI-core
    role; candidate for a "high-composite single-gate-miss → REVIEW" softening.
  - AI Content Editor: composite 0.75, jd_coverage gate failed → REJECT.

## Decision: do NOT promote to hard-gating yet

Flipping shadow → hard-gating now would regenerate/block ~36% of recommendations with
no validated improvement path. Required before promotion:

1. **Classify the 4 REJECTs** true-positive vs false-positive (inspect the JDs + skill
   sets, especially the two borderline 0.84/0.75 cases).
2. **Wire and verify a real regeneration fallback** — today `action="regenerate"` is only
   logged; hard-gating must actually re-run the recommender and re-judge, with a bounded
   retry and a graceful degradation if it still fails (Failure-First Design).
3. **Review the verdict-band calibration** with Luda: confirm a high composite (e.g. ≥0.80)
   with a single failed gate should be REVIEW rather than REJECT.
4. Re-run this sweep after any calibration change; promote only when the REJECT set is all
   true-positive and the fallback is proven.

---

## ADDENDUM (same day): the real root cause was judge run-to-run variance

Classifying the 4 REJECTs above showed the verdicts were **not reproducible**. Re-running the
judge on identical input (pinned gpt-4.1, temperature 0.0) produced different verdicts. Measured
5 runs per role:

| Role | Composites (5 runs) | Verdicts | Spread |
|---|---|---|---|
| Senior Frontend Engineer | 0.80 0.78 0.78 0.78 0.78 | REJECT ×5 | 0.02 |
| AI Security Engineer | 0.63 0.67 0.74 0.63 0.68 | REJECT ×5 | 0.11 |
| AI Content Editor | 0.76 0.77 0.69 0.76 0.80 | REJECT×4 REVIEW×1 | 0.12 |
| Learning & Development | 0.79 0.59 0.56 0.57 0.86 | ACCEPT / REVIEW / REJECT | **0.29** |

The LLM judge layer has material variance even at temperature 0.0 (OpenAI models are not bitwise
deterministic). The deterministic scorer was faithful; it was scoring a single noisy sample. This
is the months-long "Halyna flicker" root cause and a Trust-Before-Intelligence **determinism**
violation at the Intelligence layer.

**Fix (PR #3):** `evaluate_recommendation_stable()` ensembles the judge — K samples (default 5),
median-aggregate each parameter, then the canonical gate; a disagreement guard routes any
non-unanimous panel to ACCEPT_WITH_REVIEW. Validated on prod: the 4 flaky rejects resolve to **3
unanimous REJECTs + 1 routed-to-review**, no flipping.

### Reclassification of the original 4 REJECTs (now stable)
- **Senior Frontend Engineer — TRUE reject.** AI skills (eval types, prompt debugging,
  explainability UX) don't fit a frontend IC role; role_fit 0.4 (2/5 skills relevant).
- **AI Security Engineer — TRUE reject.** Genuine coverage gap: threat modeling and model access
  controls (in the JD) are not in the recommended set.
- **Learning & Development — TRUE reject.** Low gap_validity (0.4) + partial JD coverage.
- **AI Content Editor — borderline → human review.**

These are **recommender-quality** issues to fix upstream, not judge noise. Updated path to
hard-gating: the gate is now trustworthy, so (1) is done. Remaining: wire the regeneration
fallback, optionally cache verdicts by input hash for full determinism, then promote.
