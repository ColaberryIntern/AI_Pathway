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
