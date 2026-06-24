# Chapter Content Breadth + Depth Rubric (v1)

Status: active. Owner: AI Pathway. Created 2026-06-23 (weekly sync action item).

This is the rubric Luda flagged as missing from the 6/9 spec: the explicit
parameters and level anchors by which a generated chapter is judged for
**breadth** (does it cover enough of the skill at the target level?) and
**depth** (does it go deep enough for the target level?).

## Trust-Before-Intelligence contract

The judge LLM produces ONLY per-criterion integer scores (1-5) and a short
justification per chapter. It never computes the composite or the gate. A
deterministic Python step (`chapter_breadth_depth_judge.compose_score`)
normalizes the scores, applies the weights, computes the per-dimension and
overall composites, and decides the verdict color. The LLM does not grade its
own arithmetic. The judge model is pinned via `settings.judge_model`
(`get_judge_provider()`), independent of the content generator.

## Dimensions, criteria, weights

Each criterion is scored 1-5 by the judge against the level anchors below.
Python normalizes `n -> (n - 1) / 4` to a 0..1 scale.

### BREADTH (dimension weight 0.40, gate 0.60)

| Criterion | Weight | What it measures |
|---|---|---|
| `concept_coverage` | 0.50 | Range of distinct concepts / sub-skills covered vs. what the skill requires at the target level. Not one idea repeated. |
| `scenario_grounding` | 0.25 | The scenario establishes a realistic, role-relevant context that spans the skill's actual applications, not a single toy case. |
| `example_variety` | 0.25 | Examples cover more than one angle (e.g. example_1 iteration AND example_2 comparison are present and distinct). |

### DEPTH (dimension weight 0.60, gate 0.60)

| Criterion | Weight | What it measures |
|---|---|---|
| `conceptual_depth` | 0.25 | Explanations go past definitions into mechanism / why (concept card body + analogy, `why_it_matters`). |
| `worked_example_rigor` | 0.25 | Examples show genuine iteration, diagnosis, and before/after with ratings - not a single static sample. |
| `application_rigor` | 0.25 | `agent_build` + `implementation_task` require real application at the target level, not a trivial exercise. |
| `level_alignment` | 0.25 | Depth matches the `current_level -> target_level` jump: not shallow for the target, not over the learner's head. |

## Level anchors (apply to every criterion)

- **5 - Exemplary:** fully meets the target level; an expert reviewer would ship it as-is.
- **4 - Strong:** meets the target level with minor gaps.
- **3 - Adequate:** acceptable but visibly thin in places; would benefit from another pass.
- **2 - Weak:** below the target level; a learner would notice it is shallow or narrow.
- **1 - Failing:** absent or wrong for the target level.

## Deterministic composition

```
breadth  = 0.50*concept_coverage + 0.25*scenario_grounding + 0.25*example_variety   (each normalized 0..1)
depth    = 0.25*conceptual_depth + 0.25*worked_example_rigor + 0.25*application_rigor + 0.25*level_alignment
overall  = 0.40*breadth + 0.60*depth
```

## Gate / verdict policy (computed in Python)

Per chapter:

- **GREEN** when `overall >= 0.70` AND `breadth >= 0.60` AND `depth >= 0.60`.
- **YELLOW** (accept with review) when `overall >= 0.55` but a gate or the GREEN
  bar is not met.
- **RED** when `overall < 0.55`, OR a hard structural floor is violated (see below).

The agent's overall color = worst per-chapter color (standard
`color_from_findings`): any RED chapter -> RED, else any YELLOW -> YELLOW, else GREEN.

## Hard structural floors (deterministic, no LLM)

These run even when the LLM is unavailable and cap the score:

- Missing `scenario` OR `concepts` section entirely -> **RED** (ERROR finding).
- Missing any other required section (`meta`, `example_1`, `agent_build`) -> **YELLOW** (WARN).
- `scenario.narrative` shorter than 50 words -> **YELLOW** (WARN, breadth/depth thin).
- Fewer than 3 `concepts.cards` -> **YELLOW** (WARN, narrow breadth).

## Calibration (Lexicon dimension)

Calibrate against a golden set of human-rated chapters before trusting absolute
scores; pin the judge model. Re-calibrate on any judge-model change (a strategic
decision per CLAUDE.md). Tune thresholds against the golden set, not by feel.
