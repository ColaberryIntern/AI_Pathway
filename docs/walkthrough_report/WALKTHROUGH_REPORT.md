# AI Pathway - Visual Changes Walkthrough Report

Generated: 508024.0

**Tool URL:** http://95.216.199.47:3000

**Test profile created for this report:** `ee4279e2-fa46-4ad5-ac60-2e0150047869` (kept alive for review)
**Test learning path:** `ba8387e4-d02e-4917-861c-0f032dd03f36`
**Test lesson:** `34a3041f-00d3-4742-9add-8322bfcbd038`

Each section below covers one visual change. The screenshot shows the change with a red rectangle around the affected element.

---

## 1. Homepage simplified

**Live URL:** http://95.216.199.47:3000/

**To see this change:** Open the URL above.

![Homepage simplified](screenshots/01_homepage_simplified.png)

**What was changed:**

Removed 'How It Works' section and 'Ready to start your AI learning journey?' CTA block.

**Why:**

Per Luda Apr 15: page should fit on a single screen. Was previously requiring multiple scrolls.

**Files modified:**

- `frontend/src/pages/HomePage.tsx`

---

## 2. Profiles page copy update

**Live URL:** http://95.216.199.47:3000/profiles

**To see this change:** Open the URL above.

![Profiles page copy update](screenshots/02_profiles_copy.png)

**What was changed:**

Subhead changed from 'Create and manage learner profiles' to 'Create profiles for different career goals'.

**Why:**

Per Luda Apr 15: language tailored for individuals creating multiple profiles for themselves.

**Files modified:**

- `frontend/src/pages/ProfileSelectionPage.tsx`

---

## 3. Skill selection + self-assessment merged

**Live URL:** http://95.216.199.47:3000/analysis/ee4279e2-fa46-4ad5-ac60-2e0150047869

**To see this change:** Open the URL above.

![Skill selection + self-assessment merged](screenshots/03_skills_review_merged.png)

**What was changed:**

Combined two previously separate pages (skill selection, then self-assessment) into one unified page. When a skill is selected, the proficiency rating appears inline below it.

**Why:**

Per Luda Apr 15: reduce step count and let user adjust skills + ratings in one view.

**Files modified:**

- `frontend/src/pages/AnalysisPage.tsx`
- `frontend/src/components/SelfAssessment.tsx`

---

## 4. Hover tooltip with ontology description on skill name

**Live URL:** http://95.216.199.47:3000/analysis/ee4279e2-fa46-4ad5-ac60-2e0150047869

**To see this change:** Open the URL above, then hover over a skill name.

![Hover tooltip with ontology description on skill name](screenshots/04_skill_hover_tooltip.png)

**What was changed:**

Skill names now have a dotted underline + cursor:help. Hovering shows the canonical ontology description and skill_id in a dark tooltip.

**Why:**

Per Vivek Apr 29 (confirmed Agreed): users shouldn't have to guess what a skill means. Show the authoritative ontology definition on hover.

**Files modified:**

- `frontend/src/components/SelfAssessment.tsx`
- `frontend/src/pages/AnalysisPage.tsx`

---

## 5. Detected Role -> Targeted Role rename

**Live URL:** http://95.216.199.47:3000/analysis/ee4279e2-fa46-4ad5-ac60-2e0150047869

**To see this change:** Open the URL above.

![Detected Role -> Targeted Role rename](screenshots/05_targeted_role_label.png)

**What was changed:**

Label 'Detected role' renamed to 'Targeted role' throughout the tool.

**Why:**

Per Luda Apr 15: 'Targeted' is more accurate - the user is selecting a target, not having a role 'detected'.

**Files modified:**

- `frontend/src/components/profile/TargetGoalPanel.tsx`

---

## 6. End-of-page messaging when skills match target

**Live URL:** http://95.216.199.47:3000/analysis/ee4279e2-fa46-4ad5-ac60-2e0150047869

**To see this change:** Open the URL above.

![End-of-page messaging when skills match target](screenshots/06_skill_match_messaging.png)

**What was changed:**

Changed messaging from 'we will proceed with the remaining X skills' to 'we will add other relevant skills to build a learning path consisting of 5 chapters'.

**Why:**

Per Luda Apr 28: clarify that the system backfills with new skills rather than just dropping the matched ones.

**Files modified:**

- `frontend/src/pages/AnalysisPage.tsx`

---

## 7. Learning dashboard auto-activates (no Ready to Start gate)

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36

**To see this change:** Open the URL above.

![Learning dashboard auto-activates (no Ready to Start gate)](screenshots/07_learning_dashboard_no_gate.png)

**What was changed:**

Removed 'Ready to Start Learning?' confirmation page that previously appeared between skill review and the dashboard. Path now auto-activates on load.

**Why:**

Per Luda Apr 28: the gate page was duplicative of the skill review confirmation. Goes straight to the chapters.

**Files modified:**

- `frontend/src/pages/LearningDashboardPage.tsx`

---

## 8. Your Journey Roadmap page removed

**Live URL:** http://95.216.199.47:3000/analysis/ee4279e2-fa46-4ad5-ac60-2e0150047869

**To see this change:** Open the URL above.

![Your Journey Roadmap page removed](screenshots/08_journey_roadmap_removed.png)

**What was changed:**

Removed the entire 'Your Journey Roadmap' page that previously appeared between skill review and the learning dashboard. Continue to Learning Path button now goes straight to the chapters.

**Why:**

Per Luda Apr 28: the roadmap page was duplicative - same info already shown on the skill review page.

**Files modified:**

- `frontend/src/pages/AnalysisPage.tsx`

---

## 9. Chapter section navigation (6 sections, 15 min)

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above.

![Chapter section navigation (6 sections, 15 min)](screenshots/09_chapter_section_nav.png)

**What was changed:**

Chapter renderer shows 6 section tabs at top: Scenario (2m), Concepts (3m), Example 1 (3m), Example 2 (4m), Build (3m), Assignment (30m). The Assignment tab is the new 6th section.

**Why:**

Per Vivek's chapter spec (5 sections totaling 15 min) + user's request to bring back the Implementation Task assignment workflow as a 6th section.

**Files modified:**

- `frontend/src/components/chapter/ChapterRenderer.tsx`
- `backend/app/agents/chapter_generator.py`
- `backend/app/data/chapter-generator-prompt.md`

---

## 10. Chapter title uses ontology canonical name

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above.

![Chapter title uses ontology canonical name](screenshots/10_chapter_title_ontology_name.png)

**What was changed:**

Chapter title now displays the ontology canonical skill name (e.g. 'Prompt debugging & iteration') instead of the LLM-generated story title (e.g. 'Iterating on Prompts: From Literacy to Practitioner'). The story title moved to subtitle position.

**Why:**

Per Vivek Apr 29 (confirmed Agreed) on Luda's request: skills should be named consistently using ontology names throughout the tool.

**Files modified:**

- `frontend/src/components/chapter/ChapterRenderer.tsx`

---

## 11. Concepts section with mnemonic + pull_quote

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above, then click the **Concepts** tab.

![Concepts section with mnemonic + pull_quote](screenshots/11_concepts_with_mnemonic.png)

**What was changed:**

Concepts section now requires a mnemonic field (e.g. 'IVL'), a pull_quote (single memorable sentence), and 2-4 concept cards each with identifier, word, headline, body, analogy, color_role.

**Why:**

Per Vivek's depth spec: chapters lacked structural depth. Mnemonic + pull_quote are anchor elements that help retention.

**Files modified:**

- `backend/app/data/chapter-generator-prompt.md`
- `backend/app/agents/chapter_generator.py`

---

## 12. Example 1 with 3-step structure (diagnosis_checklist / prompt_variant / log_entry)

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above, then click the **Example 1** tab.

![Example 1 with 3-step structure (diagnosis_checklist / prompt_variant / log_entry)](screenshots/12_example1_steps_array.png)

**What was changed:**

Example 1 now requires a steps array with EXACTLY 3 entries: (1) diagnosis_checklist with broken/clear status flags, (2) prompt_variant ref, (3) log_entry table with key/value pairs (prompt_id, change, output_quality, lesson, reuse).

**Why:**

Per Vivek's spec: Example 1 should walk learner through the diagnostic process, not just show a prompt and result. The structured steps reinforce the methodology.

**Files modified:**

- `backend/app/agents/chapter_generator.py`
- `backend/app/data/chapter-generator-prompt.md`
- `frontend/src/components/chapter/ChapterRenderer.tsx`

---

## 13. Example 2 A/B comparison

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above, then click the **Example 2** tab.

![Example 2 A/B comparison](screenshots/13_example2_ab_comparison.png)

**What was changed:**

Example 2 must have a comparison object with test_question, exactly 2 variants (id A, id B) with full prompt/output/rating/why, and a takeaway.

**Why:**

Per Vivek's spec: Example 2 demonstrates the target-level skill (A/B testing) by example, not just description.

**Files modified:**

- `backend/app/agents/chapter_generator.py`
- `backend/app/data/chapter-generator-prompt.md`

---

## 14. Build Your Agent section

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above, then click the **Build** tab.

![Build Your Agent section](screenshots/14_agent_build_section.png)

**What was changed:**

Agent Build section requires: 3 capability_chips, 3 personalization_fields (text/textarea inputs), a system_prompt_template that interpolates the {key} placeholders, usage_steps, and final_affirmation tying back to the rubric.

**Why:**

Per Vivek's spec: each chapter ends with a takeaway artifact the learner can use the same day.

**Files modified:**

- `backend/app/agents/chapter_generator.py`
- `frontend/src/components/chapter/ChapterRenderer.tsx`

---

## 15. Try-in-LLM buttons (Run in ChatGPT)

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above, then click the **Example 1** tab.

![Try-in-LLM buttons (Run in ChatGPT)](screenshots/15_try_in_llm_buttons.png)

**What was changed:**

Added 'Run in ChatGPT' / 'Run in Claude' buttons next to every prompt in the chapter: original_prompt, iterated_prompt, A/B variants, and the interpolated agent build template. Listens to llm-changed event so labels update when user switches LLM.

**Why:**

Per Vivek Apr 29: 'I also liked aspects of your previous build especially around giving links to try out the prompts in chatgpt or claude.' Brought back from the older build.

**Files modified:**

- `frontend/src/components/chapter/ChapterRenderer.tsx`

---

## 16. Implementation Task as 6th section (NEW)

**Live URL:** http://95.216.199.47:3000/learn/ba8387e4-d02e-4917-861c-0f032dd03f36/lesson/34a3041f-00d3-4742-9add-8322bfcbd038

**To see this change:** Open the URL above, then click the **Assignment** tab.

![Implementation Task as 6th section (NEW)](screenshots/16_implementation_task_section.png)

**What was changed:**

Brought back the Implementation Task assignment workflow as a 6th chapter section. Includes title, description, 3-5 requirements, deliverable, tools (free/paid badges), evidence_requirements (file uploads), 30-60 min estimate. Submit & Get Graded uses the existing AI grading endpoint. Mentor briefing step hidden via hideMentorStep prop.

**Why:**

Per user's Apr 30 request: the assignment functionality from the old multi-lesson format was missing. Vivek's chapter format only had the Build section (which produces an agent template), not a graded assignment that produces an artifact.

**Files modified:**

- `backend/app/agents/chapter_generator.py`
- `backend/app/data/chapter-generator-prompt.md`
- `frontend/src/components/chapter/ChapterRenderer.tsx`
- `frontend/src/components/learning/ImplementationTaskCard.tsx`

---

## 17. Deterministic skill ordering between runs

**Live URL:** http://95.216.199.47:3000/analysis/ee4279e2-fa46-4ad5-ac60-2e0150047869

**To see this change:** Open the URL above.

![Deterministic skill ordering between runs](screenshots/17_deterministic_skill_ordering.png)

**What was changed:**

Set profile_analyzer LLM call to temperature=0 (was 0.3). Combined with already-zero temperature on JD parser and gap analyzer. Verified across 20 consecutive runs - identical top 5 every time.

**Why:**

Per Luda Apr 28: she ran Jennifer C twice and got different top 5 skills. The variance came from the profile analyzer's LLM call running at a non-zero temperature.

**Files modified:**

- `backend/app/agents/profile_analyzer.py`

---
