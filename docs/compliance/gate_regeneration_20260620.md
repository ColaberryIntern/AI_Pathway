# Regeneration fallback — validation (2026-06-20)

The ensembled judge gives a stable verdict, but a REJECT on its own leaves the
learner with nothing. To make hard-gating safe, the gate now **regenerates**: on
REJECT it drops the judge-flagged weak skills (majority `fit_level` not
`role_specific` across the K-run ensemble) and pulls in the next-ranked candidates
from the pool the recommender already produced (`enriched`), then re-judges. Bounded
retries; graceful degradation to the best attempt (flagged `needs_human_review`) if
the budget is spent.

Module: `backend/app/services/recommendation_gate.py` (`gated_recommendation`).
Wired into the analysis route behind `judge_gate_mode` (`shadow` default / `enforce`).

## End-to-end validation against the live judge (K=3, max_attempts=3)

Run on two roles that the single-shot gate stably rejected, using the real gpt-4.1
ensemble + the stored candidate pool (`top_10_target_skills`).

### AI Security Engineer (pool = 10)
| Attempt | Skills | Verdict | Composite | Weak (swapped out) |
|---|---|---|---|---|
| 1 | SEC.001, SEC.002, SEC.003, FND.001, PRM.003 | REJECT | 0.66 | SEC.003, FND.001, PRM.003 |
| 2 | SEC.001, SEC.002, **SEC.000, PRQ.010, SEC.012** | **ACCEPT** | **0.88** | — |

A coverage-gap REJECT became a clean ACCEPT by swapping in stronger security skills.

### Senior Frontend Engineer (pool = 8)
| Attempt | Skills | Verdict | Composite | Weak (swapped out) |
|---|---|---|---|---|
| 1 | EVL.001, ACODE.003, PRM.003, PRD.010, PRD.002 | REJECT | 0.78 | EVL.001, PRM.003, PRD.010 |
| 2 | **PRM.020, SEC.003, EVL.010**, ACODE.003, PRD.002 | ACCEPT_WITH_REVIEW | 0.90 | PRM.020 |

The generic-for-a-frontend-role AI skills were swapped out; composite rose 0.78 →
0.90 and the result is routed to a human (one replacement still borderline).

## Conclusion
Hard-gating is now **reachable and safe**: the gate self-heals rejected
recommendations from the existing candidate pool, only falling back to a
human-review flag when regeneration can't clear the bar — the learner is never left
empty-handed. Remaining before flipping `judge_gate_mode=enforce` in prod:
1. Surface `needs_human_review` in the UI / a review queue (frontend change).
2. Watch enforce-mode latency (K x attempts judge calls per analysis) and tune K /
   max_attempts; consider caching verdicts by input hash.
3. Deploy via a `main`-based release behind Gate 1 + Gate 2.
