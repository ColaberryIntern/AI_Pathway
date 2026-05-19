# Persona verification run log

Every time we re-trigger a persona's analysis through a newer engine version,
we record the new Goal/Path IDs here without deleting the originals. This
preserves the EXACT state Luda originally tested so any finding can be
reproduced against the original data, while the latest record reflects what
the current engine would produce for the same input.

The `/api/analysis/results/{profile_id}` endpoint always returns the LATEST
goal by `created_at`, so the engine's current state is what surfaces in the
UI. The originals stay queryable by Goal ID for audit.

## Dorothy Fatunmbi

| Goal ID | Path ID | Created | Engine state | Audit notes |
|---|---|---|---|---|
| `95ce0857-0613-4afa-b0b6-cef05e895c1f` | `dc6b05fb-d7b0-440f-9bdc-f252b31f8be2` | 2026-05-16 | pre-P0 | What Luda originally tested. Three issues filed: ontology rubric gap, module name mismatch, chapter-routing bug. |
| `3556e1ba-a106-4fdd-9b9f-de59a5f565bc` | `476879fe-dcb4-4f49-b564-a5f56bad4777` | 2026-05-19 | post-P1 rubric scorer | First verification run. SK.DOM.EDU.001 now at #1; SK.COM.005 at #3. SK.COM.003 still at #9 (rubric-correct: high target level penalty). |

## Halyna Mushak

| Goal ID | Path ID | Created | Engine state | Audit notes |
|---|---|---|---|---|
| `533a8602-29f1-40a3-a389-a70c45e543e8` | `76eb52fa-605f-4ff2-916d-5af1af4616c4` | 2026-05-19 (morning) | pre-fix (Luda's original test) | Skills page showed shallow set; SK.LRN.002 appeared in dashboard but not Top 5 page. |
| `39c71086-4541-47f5-9f64-43d49214c8d7` | `75c03d7f-74d8-4257-ab74-c3a6c5c2f2a5` | 2026-05-19 (afternoon, P0+May 19 fix) | post-selected_skill_ids fix | Verified chapter ordering matches user selection. |
| `4da5eb80-81bc-434d-96bc-5eb4bfb1d2de` | `f589adbd-23a4-4cbb-a830-f157e3d41bb9` | 2026-05-19 (evening, P1 rubric scorer) | post-P1 rubric scorer | SK.DOM.MKT.001 now at #1. Customer Voice still flags depth concern matching Luda's literal quote - foundational PRM 000-006 not surfacing in top 10. |

## Brittany White

| Goal ID | Path ID | Created | Engine state | Audit notes |
|---|---|---|---|---|
| (none yet) | (none yet) | - | - | Profile exists but no Goal/Path activated through the production UI. Persona corpus tests run against parseJDSkills directly. |

## Jennifer C LK May 9

| Goal ID | Path ID | Created | Engine state | Audit notes |
|---|---|---|---|---|
| `847c71a9-e866-4750-8f76-3cf934708288` | `10a04235-5983-4128-8a0a-7a097ae003d4` | 2026-05-09 | original demo state | Luda demoed with positive feedback. |

## Process

When a persona's stored analysis is out of date relative to engine improvements:

1. Run `python /app/trigger_persona_replay.py <persona_id> [<persona_id> ...]` inside the backend container. The script preserves prior records.
2. Add a new row above with the new Goal ID, Path ID, and a one-line note about what changed in the engine.
3. Run `python /app/run_qa_team.py <persona_id>` to verify the new state.
4. The UI will start serving the new analysis on the next page load.

Original data is never deleted, so we can always reproduce the exact state Luda saw at any point.
