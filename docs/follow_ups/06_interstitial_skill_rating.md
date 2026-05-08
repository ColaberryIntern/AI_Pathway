# Item 06 - Interstitial proficiency-rating step for swapped-in skills

**Source:** Luda's walkthrough feedback, 2026-05-08, item `06_skill_match_messaging`.
**Priority:** Deferred per Luda ("The #6 can be done later"). Not blocking the Jennifer demo.
**Owner:** Claude / Ali to schedule after the demo round.

## What Luda asked for (verbatim)

> "When we add skills if the user's proficiency matches the target level, I think that we need to show another page with 5 skills, 2 remaining with selected proficiency levels and 3 added (skills 6,7,8) for the user to rate the proficiency for skills 6,7 and 8. In other words, we always wants to ask the user to select/deselect what they want on the path and select their proficiency levels. And only then go to generate the chapters. The skills that matched the target level can remain on the page at the bottom."

## Current behavior

`frontend/src/pages/AnalysisPage.tsx` step `skill_selection` shows the user the top 5 skills parsed from the JD and lets them rate proficiency. If some of those rated proficiencies hit target level, the system swaps in replacement skills from the wider gap list and proceeds straight to chapter generation. The user never gets to rate the swapped-in skills.

## Required behavior

A new interstitial page (or step within `skill_selection`) that triggers when at least one of the initial top 5 was rated at target. The page must:

1. **Show the user's final 5-skill path:** the N skills they rated below target (kept) plus the (5 - N) replacement skills pulled from the gap list (added).
2. **Let the user rate proficiency on the newly-added skills.** Same rating UI that already exists for the original top 5.
3. **Let the user select/deselect** any skill from the path (so they can drop one of the auto-added ones if they prefer something else).
4. **Show a "matched-level skills" section at the bottom** — the original skills they already had at target. Read-only, just for context.
5. **Only after the user confirms ratings on all 5 path skills**, proceed to chapter generation.

## Files likely touched

- `frontend/src/pages/AnalysisPage.tsx` — new step state (e.g. `'rate_replacement_skills'`) inserted between `skill_selection` and `analyzing` / chapter generation.
- `frontend/src/components/SelfAssessment.tsx` — already has the rating UI; should be reusable for the new page.
- `backend/app/agents/profile_analyzer.py` — possibly: distinguish "initial top 5" from "final 5 after replacement" in the response, so the frontend knows which subset to ask the user to rate.
- `backend/app/api/routes/analysis.py` — endpoint may need an extra round-trip if the user changes the path during the new step.

## Open design questions

1. **Where exactly does the swap happen now?** Need to trace the flow from `parseJDSkills` -> `analysis/full` -> rendered top 5 to confirm where the "if rated at target, pull a replacement" logic lives. Likely in the analyzer or in the React state right after rating.
2. **Should the replacement skills come from the existing `top_10_skills` parsed list, or from the wider ontology gap?** The current behavior is unclear; need to verify before extending.
3. **What if the user deselects one of the replacements?** Do we offer another replacement, or do we accept a 4-skill path? Default to "offer another from the gap list" but confirm with Luda.

## Verification plan

1. Set up a Jennifer C profile and intentionally rate the first top 5 at or above target on at least one skill. (May need a profile crafted to make this likely.)
2. Confirm the new interstitial page renders with 2 retained + 3 added.
3. Rate proficiency on the new ones and continue.
4. Walk through to chapter generation and confirm the path reflects the user's final selections + ratings.
5. Add a screenshot of this new step to `walkthrough_report.py` `CHANGES` for the next round so Luda can sign off.

## Related notes

- Luda also approved the message change inside item 06 ("we will add other relevant skills to build a learning path consisting of 5 chapters"). That part is already shipped and does not need rework.
- This work touches `?view=skill_selection` URL state added 2026-05-07 — confirm that URL still lands sensibly when the new interstitial step is in flight.
