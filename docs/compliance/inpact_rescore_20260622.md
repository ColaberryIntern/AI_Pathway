# INPACT re-score - 2026-06-22 (after Phase 0 + 1 + 2)

Re-scores the system on Ram's 1-6 scale (/36 x 100) after the compliance work, against
the 2026-06-20 baseline of **17/36 = 47%**. Method: score each dimension by what is now
in `main` (merged) with test/validation evidence; cap a dimension where a gate to the
top score is an owner action (credentials, enforce flip) or standing work (ontology).

## Scorecard

| Dimension | Baseline | Now | Basis for the new score |
|---|---|---:|---|
| Instant | 3 | **3** | Batch analysis in seconds; real-time isn't the use case. LLM timeouts make latency *bounded/predictable*, but enforce-mode gating adds latency, so net unchanged. |
| Natural | 3 | **4** | Judge pinned to gpt-4.1 (calibration showed gpt-4o under-reads JDs) + golden/drift guard keep JD reading correct; typed input contracts validate the parse boundary. Capped <5 by the standing ontology gaps. |
| Permitted | 3 | **4** | Deterministic + calibrated judge gate is wired into the prod recommendation path (shadow) and a regeneration fallback makes hard-gating reachable + safe (validated on real rejects). Capped at 4 because it runs in **shadow**, not enforce - it observes but does not yet block. -> 5 on the enforce flip. |
| Adaptive | 2 | **5** | The root-cause dimension, now strongest. Judge **pinned + calibrated** (lexicon + golden anchor), **drift check** + documented recalibration trigger, **ensemble** that fixes the temperature-0 verdict variance, and a **self-correcting regeneration** loop. Capped <6 by the absence of a learner-outcome feedback loop + automated periodic drift scheduling. |
| Contextual | 3 | **4** | Enumeration/verdict variance fixed by the ensemble; correlation IDs carry context end-to-end; the RAG no-op is now **observable** (`/health` + `get_rag_status`) instead of silent. Capped <5 because RAG retrieval is still a no-op until GCP credentials are provisioned. |
| Transparent | 3 | **5** | Structured JSON logging, correlation IDs propagated into every LLM-call telemetry line (duration_ms, status, error_class), per-request telemetry, `/health` with RAG status, and gate verdicts logged with stability metadata. Capped <6 by the lack of persisted/queryable metrics + rolling success/latency dashboards. |
| **Total** | **17 / 36 (47%)** | **25 / 36 (69%)** | Moderate-Trust band; **+22 points**. Engineering for compliance is done; the last ~11 points to >= 80 are owner/standing actions (below). |

## What each phase moved
- **Phase 0** (judge pinned + calibrated + deterministic gate in prod, assessment trust-site): Adaptive 2->4 (foundation), Permitted 3->4.
- **Phase 1** (observability + external-call hardening): Transparent 3->5, supported Contextual/Natural.
- **Phase 2** (tests, typed contracts, golden + drift, RAG diagnosis/observability): Adaptive 4->5, Natural 3->4, Contextual 3->4, plus the test/contract `Solid` underpinning.

## Path from 69% to >= 80% (>= 29/36)
All three are **owner / standing** actions, not new engineering:

1. **Provision GCP credentials** so RAG retrieves for real -> **Contextual 4 -> 5** (+1). (item 10's true fix)
2. **Flip `judge_gate_mode=enforce`** in prod after watching shadow verdicts + surfacing `needs_human_review` in the UI -> **Permitted 4 -> 5** (+1).
3. **Close the standing ontology gaps** (skill coverage/mappings) -> **Natural 4 -> 5** (+1).

That reaches **28/36 = 78%**. The final point to clear 80 comes from one more increment on either:
- **Transparent 5 -> 6**: persist telemetry to a queryable store + rolling success/latency/error-rate dashboards (the Observability framework's required metrics), or
- **Adaptive 5 -> 6**: a learner-outcome feedback loop + scheduled automated drift checks.

Either gives **29/36 = 81%**, crossing the production line with zero P0/P1 gaps open.

## Standing governance note
The "name INPACT dimensions + 7 layers in PROGRESS.md for every AI change" rule is now being followed on the compliance PRs; it should be enforced as a PR checklist item going forward (the last open governance gap from the original plan's rule table).
