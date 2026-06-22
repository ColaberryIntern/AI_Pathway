# Ontology gap audit - 2026-06-22 (Natural +1 input)

Read-only structural audit of `backend/app/data/ontology.json` (v2.1) to scope the
Natural-dimension ontology-depth work. Reproduce: `cd backend && py -3.12 scripts/ontology_gap_audit.py`.

## Headline
The ontology is **structurally sound** but **has no per-skill descriptions**.

| Check | Result |
|---|---|
| Skills / domains / proficiency levels | 220 / 25 / 6 |
| Skills with EMPTY `rubric_by_level` | **0** (clean - the May-16 bug class stays fixed) |
| Skills with < 6 rubric levels | 0 |
| Orphan prerequisites (prereq id not a real skill) | 0 |
| Domains with zero skills | 0 |
| Thin domains (<= 3 skills) | 0 |
| **Skills with a `description` field** | **0 / 220** |

## The one real gap: missing skill descriptions
Every skill has `id`, `name`, `level`, `prerequisites`, and a full 6-level
`rubric_by_level`, but **none has a `description`** (a prose "what is this skill and
why does it matter"). Code that reads `skill.get("description")` (rubric_scorer,
linkedin_parser, the analysis enrich step) therefore always gets `""`, and the Top-5
hover tooltip's skill-definition line is empty (it falls back to the rubric text,
which is why this was never loud). Adding descriptions would:
- enrich the Top-5 tooltips (the Jennifer-C "why these skills" surface),
- give the judge + content generator more grounded per-skill context (Natural),
- make the lexicon crisper (helps the judge's role-fit reading - the drift check's
  role_fit 0.143 sat near tolerance).

This is the highest-leverage Natural +1 item and is **SME/content work** (Luda/Vivek
write the prose; it is not an engineering decision).

## Secondary (depth, not breadth)
Coverage breadth is fine - every domain has 4-17 skills. The smallest are
`D.SYNTH` (4 - Synthetic Data & Flywheel), `D.VOICE` (5 - Voice AI), `D.LRN`
(5 - Learning & Adaptation). If any of those verticals become target roles, consider
adding a few skills; none is urgent today.

## Recommendation
1. **Add `description` to all 220 skills** (SME pass with Luda/Vivek). Biggest Natural
   lift; turns empty tooltips + thin lexicon into grounded context. I can scaffold a
   template (id, name, current rubric L1/L6 anchors) to make the SME pass fast, and
   wire the field through once the prose exists.
2. Backfill `D.SYNTH` / `D.VOICE` / `D.LRN` only if those become demoed roles.
3. Re-run `judge_drift_check` after descriptions land - richer context may pull the
   role_fit reading up off the 0.15 tolerance edge.
