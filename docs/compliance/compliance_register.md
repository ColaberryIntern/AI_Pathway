# AI Compliance Register

Closes the last governance item in the Definition of Compliant: *every AI component
in a register with its INPACT dimensions, 7-layer touchpoints, deterministic-compute
status, and test status*. Keep this current - the PR checklist at the bottom enforces
it on new AI work.

Legend - **Det?**: is everything the LLM would self-report computed deterministically
in code? (Y / N / n/a = no LLM). **Tests**: dedicated test file present.

## Governance + judging (the trust core)

| Component | Role | INPACT | 7-Layer | Det? | Tests |
|---|---|---|---|---|---|
| `services/judge_scoring.py` | deterministic scorer (composite, gates, verdict) | Permitted, Adaptive | Governance | **Y** | Y (`test_judge_scoring`, `test_judge_golden`) |
| `services/recommendation_judge.py` | judge: LLM per-item judgments only + ensemble | Permitted, Adaptive | Governance, Intelligence | **Y** | Y (`test_recommendation_judge`) |
| `services/recommendation_gate.py` | gate + regeneration fallback | Permitted, Adaptive | Governance, Orchestration | **Y** | Y (`test_recommendation_gate`) |
| `services/rubric_scorer.py` | deterministic top-5 ranker (role-essence/domain/diversity) | Permitted, Adaptive, Natural | Governance, Intelligence | **Y** | Y (`test_rubric_scorer`) |
| `qa_agents/*` (demo_gate, chapter_reviewer, customer_voice, path_coherence, skill_curator, verdict, orchestrator) | pre-demo QA gates | Permitted | Governance, Observability | **Y** (deterministic verdicts) | Partial (`test_demo_gate`, `test_chapter_reviewer`, `test_customer_voice`) |

## Analysis + recommendation agents

| Component | Role | INPACT | 7-Layer | Det? | Tests |
|---|---|---|---|---|---|
| `agents/orchestrator.py` | coordinates the workflow | Adaptive, Contextual | Orchestration | n/a (delegates) | Typed contract (`test_agent_contracts`) |
| `agents/profile_analyzer.py` | learner state (state A) | Natural, Contextual | Intelligence, Semantic | partial (normalize) | via integration tests |
| `agents/jd_parser.py` | JD -> target skills (state B) | Natural, Contextual | Intelligence, Semantic | partial | Y (`test_state_b_fallback` et al.) |
| `agents/linkedin_parser.py` | LinkedIn -> profile | Natural, Contextual | Intelligence | partial (ontology-validated) | Y (`test_linkedin_parser`) |
| `agents/assessment_agent.py` | self-assessment scoring | Permitted, Adaptive | Intelligence, Governance | **Y** (`normalize_skill_scores`) | Y (`test_assessment_normalize`) |
| `agents/gap_analyzer.py` | state A vs B gaps | Natural, Adaptive | Intelligence | partial (deterministic gap math) | via integration tests |
| `agents/learner_adjuster.py` | adjust candidates to learner | Adaptive, Natural | Intelligence | partial (guard is deterministic) | Y (`test_learner_adjuster`) |

## Content generation + curation

| Component | Role | INPACT | 7-Layer | Det? | Tests |
|---|---|---|---|---|---|
| `agents/path_generator.py` / `services/path_generator.py` | learning path/chapters | Natural, Instant | Intelligence | partial | Y (`test_journey_roadmap`, `test_gap_chapter_consistency`) |
| `agents/module_outline.py` / `agents/lesson_generator.py` / `agents/chapter_generator.py` | module/lesson/chapter content | Natural | Intelligence | partial | Y (`test_chapter_generator_v3_objectives`, `test_lesson_*`) |
| `agents/content_curator.py` | learning resources (uses RAG) | Contextual | Intelligence, Semantic | n/a | Typed contract (`test_agent_contracts`) |
| `agents/mentor_agent.py` | learner Q&A | Natural, Instant | Intelligence | n/a | Y (`test_mentor_agent`) |

## Cross-cutting infrastructure

| Component | Role | INPACT | 7-Layer | Det? | Tests |
|---|---|---|---|---|---|
| `services/llm/_resilience.py` | timeout + retry + telemetry on every LLM call | Solid, Transparent | Real-Time, Observability | n/a | Y (`test_llm_resilience`) |
| `services/llm/factory.py` + providers | pinned judge provider; provider abstraction | Permitted, Solid | Intelligence | n/a | via judge tests |
| `observability.py` + `correlation.py` + `metrics.py` | structured logs, correlation IDs, /metrics | Transparent | Observability | n/a | Y (`test_observability`, `test_metrics`) |
| `services/rag/*` (retriever, embeddings, vector_store) | RAG retrieval (no-op until GCP ADC) | Contextual | Semantic, Storage | n/a | Y (`test_rag_status`) |
| `services/ontology.py` | canonical skill ontology | Lexicon, Contextual | Semantic, Storage | Y (lookup/validation) | Y (`test_ontology_grounding`) |

## Known gaps (tracked)
- RAG: no-op until GCP credentials are provisioned (see `rag_diagnosis.md`); status visible at `/health`. Owner action.
- Deeper content-gen agents (`path_generator`, `lesson_generator`, `module_outline`, `chapter_generator`) have integration/consistency tests but not the full four-type mocked-LLM unit suite - lower priority (covered indirectly + by Gate 1/2).
- (Closed 2026-06-22) `linkedin_parser` + `mentor_agent` now have dedicated mocked-LLM tests.

## PR checklist (enforce on every AI change)
Per CLAUDE.md "name which INPACT dimensions it serves and which of the 7 layers it
touches, recorded in PROGRESS.md". For any PR that adds/changes an AI feature:

- [ ] PROGRESS.md entry names the **INPACT dimension(s)** served and the **7-layer**
      touchpoint(s).
- [ ] Anything the LLM would self-report (scores, gates, math, ID/lookup validation)
      is computed **deterministically** in code, not trusted from the model.
- [ ] Judge/evaluator changes: model pinned + calibrated; golden + drift guard updated
      if thresholds/lexicon moved (`judge_calibration.md`).
- [ ] External calls have timeout + retry + error handling (`_resilience`).
- [ ] Four mandatory test types present (happy / failure / boundary / idempotency).
- [ ] This register updated if a component was added or its status changed.
- [ ] Model-class / judge-model change -> escalated (Strategic Decision), not silent.
