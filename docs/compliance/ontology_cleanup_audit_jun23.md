# Ontology Cleanup Audit - Jun 23 weekly sync

Action item from the Jun 23 weekly sync (Luda): the ontology has grown to ~220
skills with "remnants of different things we put in and then took out"; clean it
up so it is "not all over the place," and figure out the IP angle.

Tool: `backend/scripts/ontology_cleanup_audit.py` (READ-ONLY). Run against the
prod DB inside `ai-pathway-backend-1`. Raw data: `ontology_cleanup_audit_jun23.json`.

## Headline

- **Ontology size:** 220 skills across 25 domains (version 2.1).
- **Actually used in real paths:** **66 skills (30%).**
- **Orphans (never referenced by any Module or cached Lesson):** **154 skills (70%).**
- **Structural hygiene: clean.** No skill missing a 6-level `rubric_by_level`, no
  duplicate names or ids, no empty domains, no skill pointing at an undefined
  domain. The May 16 bug class (empty rubrics) is not present.
- **Integrity: clean.** Zero skill_ids are used by modules/lessons but missing
  from the ontology, so the demo integrity sweep (Gate 1) still passes. The
  cleanup is a bloat/scope problem, not a correctness problem.

## Important caveat (why this is NOT an auto-delete list)

"Orphan" means **not yet recommended to any persona tested so far** - not
"useless." Many orphans are legitimate skills that simply have not surfaced for
the (marketing-heavy) personas run to date. Deleting a skill is:

1. **Destructive + gated** - removing a node that a future/existing path needs
   would fail Gate 1 and break content. Any prune must re-run Gate 1 + Gate 2.
2. **An IP / content judgment** owned by Luda + Vivek, not an autonomous code
   change (CLAUDE.md: model-class/content/IP decisions escalate).

So this audit delivers the **candidate list + blast radius**; the actual prune
set is a Luda/Vivek decision. Recommended approach below.

## Usage by domain (used vs orphan)

| Domain | Total | Used | Orphan |
|---|---|---|---|
| D.ACODE | 9 | 1 | 8 |
| D.AGT | 13 | 3 | 10 |
| D.COM | 6 | 4 | 2 |
| D.COMP | 6 | 0 | 6 |
| D.CTIC | 6 | 2 | 4 |
| D.DIG | 8 | 0 | 8 |
| D.DOM | 8 | 3 | 5 |
| D.EVL | 8 | 4 | 4 |
| D.FND | 17 | 8 | 9 |
| D.GOV | 10 | 5 | 5 |
| D.HRNS | 8 | 0 | 8 |
| D.LRN | 5 | 2 | 3 |
| D.MOD | 6 | 3 | 3 |
| D.MUL | 12 | 0 | 12 |
| D.OPS | 10 | 3 | 7 |
| D.PRD | 8 | 6 | 2 |
| D.PRM | 12 | 6 | 6 |
| D.PROTO | 7 | 0 | 7 |
| D.PRQ | 12 | 4 | 8 |
| D.RAG | 11 | 4 | 7 |
| D.RSN | 8 | 1 | 7 |
| D.SEC | 8 | 5 | 3 |
| D.SYNTH | 4 | 0 | 4 |
| D.TOOL | 13 | 2 | 11 |
| D.VOICE | 5 | 0 | 5 |

### Whole domains with ZERO used skills (strongest consolidation candidates)

`D.COMP` (6), `D.DIG` (8), `D.HRNS` (8), `D.MUL` (12), `D.PROTO` (7),
`D.SYNTH` (4), `D.VOICE` (5) - 50 skills across 7 domains that have never been
recommended. These are the first question for Luda/Vivek: are these intentional
future coverage, or remnants to cut?

## Recommended cleanup approach (for Luda + Vivek sign-off)

1. **Decide the keep-set, not the delete-set.** Start from the 66 used skills +
   any skills the team intends to cover deliberately (e.g. enterprise base
   curriculum, planned verticals). Everything else is a prune candidate.
2. **Quarantine before delete.** Move prune candidates to an `ontology_archive`
   section/file rather than hard-deleting, so nothing is lost and a path can
   never reference a vanished id. Reversible.
3. **Re-run the gates.** After any change to `ontology.json`: Gate 1
   (`sweep_integrity.py`) and Gate 2 (`verify_profile_e2e.py`) on the demo
   profiles, per CLAUDE.md.
4. **IP angle:** treat the curated keep-set as the proprietary ontology; archive
   the rest out of the shipped artifact.

## What was NOT done here (and why)

No ontology nodes were removed. Removal is destructive, Gate-gated, and an IP
decision for Luda + Vivek. This pass delivers the repeatable audit tool + the
candidate list so the prune can be done safely and deliberately.
