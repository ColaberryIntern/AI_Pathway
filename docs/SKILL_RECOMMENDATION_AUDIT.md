# Skill Recommendation Audit Report

**Date:** 2026-03-18
**Triggered by:** Luda Kopeikina's walkthrough of Brittany White's case
**Purpose:** Explain why the tool's skill recommendations differ from direct Claude analysis

---

## Executive Summary

Luda compared our tool's output against Claude's direct judgment for Brittany White and found:

1. The tool recommended **10 skills**; Claude (with full context) said **only 2 were necessary**
2. **AI Governance** was missing from the tool's recommendations but Claude included it
3. Brittany's **stored profile had errors** (SAP listed as current position incorrectly)

This audit traced the full pipeline and identified **7 root causes** that explain these discrepancies.

---

## The Pipeline (How Skills Flow)

```
Profile/Resume  ──→  ProfileAnalyzerAgent  ──→  State A (10 current skills)
                                                       │
Target JD       ──→  JDParserAgent         ──→  State B (10 target skills)
                                                       │
                                              ┌────────▼─────────┐
                                              │   GapAnalyzer     │
                                              │  (LLM-ranked top  │
                                              │   10 gaps)        │
                                              └────────┬─────────┘
                                                       │
                                              ┌────────▼─────────┐
                                              │  Gap Engine       │
                                              │  (deterministic   │
                                              │   formula + floors)│
                                              └────────┬─────────┘
                                                       │
                                              ┌────────▼─────────┐
                                              │  Path Generator   │
                                              │  (5 chapters,     │
                                              │   mandatory domains│
                                              │   prereqs, caps)  │
                                              └──────────────────┘
```

Each stage applies constraints that nudge the output further from pure LLM judgment.

---

## Root Causes of Divergence

### 1. Hard-Coded "Exactly 10" Constraint

**Where:** `profile_analyzer.py`, `jd_parser.py`, `gap_analyzer.py`

Both the ProfileAnalyzer and JDParser are forced to return **exactly 10 skills** via JSON schema constraints (`minItems: 10, maxItems: 10`). The GapAnalyzer also returns exactly 10 gaps.

**Why it matters:** When Luda asked Claude directly (without this constraint), Claude determined only **2 skills** were truly necessary for Brittany's transition. The tool pads to 10, diluting focus with marginally relevant skills ranked 5-10.

**This is the primary divergence.** The tool can never output fewer than 10 skills, regardless of the situation.

---

### 2. Gap Engine Floor Logic Inflates Current Levels

**Where:** `gap_engine.py` (lines 122-160)

Three floor mechanisms silently raise the learner's current levels before computing gaps:

| Floor | Rule | Effect on Brittany |
|-------|------|-------------------|
| **Professional floor** | Any L2+ skill anywhere → all unknowns start at L1 | Brittany has L3 in digital literacy → all unknown skills bumped from L0 to L1 |
| **Domain floor** | Known domain skill → other skills in that domain start at `max(1, domain_max - 1)` | If she has SK.PRM.001 at L2, other prompting skills start at L1 |
| **Skill-level floor** | L3+ anywhere AND skill is ontology L3+ → start at L2 | Advanced governance skills (L3+) get auto-bumped to L2 |

**Why it matters:** These floors **shrink deltas**. A gap Claude sees as L0→L3 (delta 3) might only show as L2→L3 (delta 1) in the tool. Smaller delta = lower priority score = buried below less important skills with bigger raw gaps.

**Brittany's governance gap:** If shrunk from delta 2 to delta 1 by the professional floor, it falls below higher-delta skills in the ranking formula.

---

### 3. Mandatory Domain Forcing

**Where:** `path_generator.py` (lines 39-47)

Every learning path is **forced** to include at least one skill from each of 4 categories:

```python
MANDATORY_CATEGORIES = [
    {"name": "foundation",  "domains": ["D.FND"]},
    {"name": "applied_ai",  "domains": ["D.PRM", "D.RAG", "D.AGT", "D.MOD", "D.MUL", "D.OPS", "D.TOOL"]},
    {"name": "evaluation",  "domains": ["D.EVL"]},
    {"name": "safety",      "domains": ["D.SEC", "D.GOV"]},
]
```

**Two problems:**

1. **The path always has 5 chapters** even when the learner only needs 2. The mandatory categories consume 3-4 slots, leaving only 1-2 slots for the truly important skills.

2. **D.GOV IS actually forced** via Phase 0.5 injection + Phase 4 post-enforcement. But it injects the **lowest-level L2+ skill** mechanically — not the most contextually relevant one. So the tool may include `SK.GOV.000` (AI governance fundamentals) instead of `SK.GOV.002` (Policy to controls mapping) which Claude would recommend for a product role.

**Note:** This is the **opposite** of Luda's concern. The tool DOES force governance, but:
- It may not appear in the **displayed top 10 gaps** (those are computed before mandatory enforcement)
- The injected skill may be too basic for the role

---

### 4. Role Template Override

**Where:** `role_templates.py`, `orchestrator.py` (lines 201-220)

**5 templates currently exist:**

| Role | Skills | Includes D.GOV? |
|------|--------|-----------------|
| AI Product Manager | 18 | Yes (SK.GOV.002, .020, .021) |
| Martech AI Product Manager | 15 | Partially (SK.GOV.020 only) |
| AI Operations Manager | 17 | Yes (SK.GOV.002) |
| Healthcare Data Scientist | 12 | Yes (SK.GOV.020, .021) |
| Machine Learning Engineer | 17 | No (relies on Phase 0.5 injection) |

When a template matches, it **overrides** the LLM's State B:

```python
for sid, level in template.items():
    valid_state_b[sid] = max(valid_state_b.get(sid, 0), level)
```

**Brittany's case:** Her target role is **"Senior AI Product Marketing Manager"** — no template matches this exact string. The closest is "AI Product Manager" but string matching is exact. So no template is applied, and the system relies on:
1. JDParser's top 10 (may not include D.GOV if the JD doesn't mention it)
2. Phase 0.5 mandatory injection (forces basic D.GOV)

**Missing templates for Luda's personas:**
- Senior AI Product Marketing Manager (Brittany White)
- AI Content Editor (Jennifer C)
- No templates exist for Dorothy, Halyna, or Srushti's target roles

---

### 5. Ranking Formula Biases Toward Large Deltas

**Where:** `gap_engine.py` (lines 168-172)

```
priority_score = (3 x delta) + (2 x role_relevance) - (0.5 x skill_level)
```

| Weight | Factor | Problem |
|--------|--------|---------|
| **3x** | Delta (gap size) | Dominates everything else |
| **2x** | Role relevance (binary 0/1) | Only +2 if domain matches target |
| **-0.5x** | Skill level | Mild penalty for advanced skills |

**Example:** A "nice to have" skill with delta=3 scores **9.0**, while a "must have" skill with delta=1 and full role relevance scores only **4.5**. The large-gap skill always wins, even if the small-gap skill is critical for the role.

**What's missing from the formula:**
- **Role criticality** — how important the JDParser rated this skill (high/medium/low)
- **Learning intent alignment** — does this match what the learner wants to learn?
- **Current AI proficiency** — a Skilled Practitioner needs different skills than a Curious Explorer

---

### 6. Profile Parsing Quality

**Where:** `profiles.py`, `profile_15_brittany_white.json`

Luda flagged that Brittany's stored profile incorrectly lists SAP as her current position. The resume parsing pipeline:
1. Accepts PDF/DOCX
2. LLM extracts structured fields
3. Stores as JSON

If the parser misidentifies current role, industry, or experience level, the ProfileAnalyzer will assess current skills incorrectly. **Garbage in → garbage out.**

**Profiles that need auditing:** All 5 of Luda's personas should be manually verified against their actual LinkedIn profiles and intake answers.

---

### 7. Learner Context Weakly Weighted

When Luda asked Claude directly, she factored in:
- Brittany's **current AI usage level** (Skilled Practitioner — uses 5+ tools)
- Her **specific intent** (Creative & Design Work)
- Her **industry context** (Marketing & Creative)
- Her **existing tool experience** (ChatGPT, Claude, Midjourney, DALL-E, Perplexity)

The tool passes `learning_intent` and `industry` to the GapAnalyzer LLM prompt, but the **gap engine's deterministic ranking formula ignores them entirely**. The formula is purely mathematical: `delta x 3 + relevance x 2 - level x 0.5`.

A Skilled Practitioner who already uses 5+ AI tools daily doesn't need foundational prompting skills, but the tool may still recommend them if the JD mentions prompting and the profile parser underestimates her current level.

---

## Side-by-Side: Tool vs. Claude

| Factor | Tool Behavior | Claude (Direct) |
|--------|--------------|-----------------|
| Number of skills | Always 10 (hardcoded) | Flexible — recommends what's actually needed |
| Current level (State A) | Floors inflate levels, shrinking gaps | Reasons from actual profile evidence |
| Target level (State B) | Role template override OR LLM top 10 | Holistic analysis of JD requirements |
| Gap prioritization | Formula: `3*delta + 2*relevance - 0.5*level` | Contextual: intent, experience, urgency |
| Governance (D.GOV) | Mechanically injected via mandatory category | Recommended when contextually appropriate |
| Path length | Always 5 chapters | Would recommend what's actually needed |
| Learner context | Passed to LLM but not in ranking formula | Central to the recommendation |

---

## Answers to Luda's Questions

### "Why does the tool give different skills than Claude?"

Because the tool applies **7 layers of constraints** that Claude doesn't have when reasoning directly:
1. Exactly-10 skill cap
2. Floor logic inflating current levels
3. Mandatory domain categories
4. Role template overrides
5. Delta-biased ranking formula
6. Prerequisite forcing
7. Domain diversity caps (max 2 chapters per domain)

Each layer nudges the result further from pure contextual judgment.

### "AI Governance was not recommended but should have been"

**Partially incorrect.** The tool DOES force D.GOV into every path via Phase 0.5 + Phase 4 mandatory enforcement. However:
- It may inject the **wrong** D.GOV skill (generic fundamentals vs. contextually relevant policy mapping)
- It may not appear in the **displayed** top 10 gaps (those are computed before enforcement)
- The displayed skills and the actual path chapters **can differ**

### "Claude says only 2 skills needed, tool gives 10"

The tool is hardcoded to 10. There is no mechanism to output fewer. Even if 8 of those 10 are low-importance padding, the system treats them all equally.

### "How should we use the Skills Selection/Prioritization Metric?"

Luda's metric captures dimensions the tool currently lacks:
1. **Role criticality** — is this skill essential or nice-to-have?
2. **Current proficiency context** — factoring in actual tool usage and experience
3. **Learning ROI** — how much impact does closing this gap create?

This could replace or augment the current gap engine formula. The current `3*delta + 2*relevance - 0.5*level` doesn't capture "learning ROI" or "role criticality" with enough granularity.

---

## Recommended Fixes

### HIGH Priority

| # | Fix | Files | Impact |
|---|-----|-------|--------|
| 1 | **Make skill count flexible (3-10)** — let the LLM decide how many are truly relevant instead of forcing exactly 10 | `profile_analyzer.py`, `jd_parser.py`, `gap_analyzer.py` | Directly addresses Luda's "10 vs 2" concern |
| 2 | **Add criticality to gap ranking** — incorporate JDParser's importance rating (high/medium/low) into the formula | `gap_engine.py` | Prevents "nice to have" large-gap skills from outranking critical small-gap ones |
| 3 | **Fix profile data** — audit all 5 personas against actual LinkedIn/intake data | `profile_15_brittany_white.json` + others | Ensures State A is accurate |

### MEDIUM Priority

| # | Fix | Files | Impact |
|---|-----|-------|--------|
| 4 | **Make path length flexible (2-5)** — don't force 5 chapters when 2 suffice | `path_generator.py` | Addresses path bloat |
| 5 | **Review mandatory domain rules** — make categories configurable per role type | `path_generator.py` | Non-technical roles may not need D.EVL at the same depth |
| 6 | **Integrate Luda's prioritization metric** — weight "role criticality" and "learning ROI" more heavily | `gap_engine.py` | Aligns tool with expert judgment |

### LOW Priority

| # | Fix | Files | Impact |
|---|-----|-------|--------|
| 7 | **Add role templates** for Luda's personas | `role_templates.py` | Better coverage for tested profiles |

---

## Appendix: Key File Locations

| File | Purpose |
|------|---------|
| `backend/app/agents/profile_analyzer.py` | State A extraction (current skills) |
| `backend/app/agents/jd_parser.py` | State B extraction (target skills) |
| `backend/app/agents/gap_analyzer.py` | LLM-based gap prioritization |
| `backend/app/services/gap_engine.py` | Deterministic gap ranking formula |
| `backend/app/services/path_generator.py` | 5-chapter path generation with mandatory domains |
| `backend/app/agents/orchestrator.py` | Coordinates all agents, applies role templates |
| `backend/app/data/role_templates.py` | Predefined target skill levels per role |
| `backend/app/data/profiles/` | Stored test profiles (16 total) |
| `backend/app/services/ontology.py` | Ontology loading and prompt formatting |
| `backend/app/data/ontology.json` | 186 skills, 22 domains, L0-L5 scale |

## Appendix: Available Test Profiles

| # | Name | File | Target Role | Has Template? |
|---|------|------|------------|---------------|
| 13 | Laura G | profile_13_laura_g.json | Martech AI Product Manager | Yes |
| 14 | Jenny Boavista | profile_14_jenny_boavista.json | AI Operations Manager | Yes |
| 15 | Brittany White | profile_15_brittany_white.json | Senior AI Product Marketing Manager | **No** |
| 16 | Jennifer Campaniolo | profile_16_jennifer_campaniolo.json | AI Content Editor | **No** |

**Missing personas from Luda's list:** Dorothy Fatunmbi, Halyna Mushak, Srushti Madhure, Beth Rochefort, Gayle G, Cami V, Moha S, Rachel C, Seetha H, Rebecca H — these need to be created as test profiles.

## Appendix: D.GOV Skills in the Ontology

| Skill ID | Name | Level | Prerequisites |
|----------|------|-------|--------------|
| SK.GOV.000 | AI governance fundamentals | 1 | SK.FND.002 |
| SK.GOV.001 | AI risk framing | 2 | SK.FND.002, SK.FND.022 |
| SK.GOV.002 | Policy to controls mapping | 3 | SK.AGT.030, SK.EVL.010 |
| SK.GOV.010 | AI regulations landscape (EU AI Act) | 2 | SK.GOV.000 |
| SK.GOV.020 | PII/PHI handling & retention | 2 | SK.FND.020 |
| SK.GOV.021 | Data minimization & anonymization | 3 | SK.GOV.020 |
| SK.GOV.022 | AI-generated content disclosure | 2 | SK.GOV.000 |
| SK.GOV.023 | EU AI Act enforcement readiness | 3 | SK.GOV.010 |
