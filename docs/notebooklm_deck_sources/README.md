# NotebookLM source pack - AI Pathway QA system enterprise deck

Everything you need to generate the enterprise slide deck on the multi-agent QA system. The files are numbered in the upload order that gives NotebookLM the strongest grounding.

## How to use this folder

1. Create a new NotebookLM notebook.
2. **Upload every file in this folder as a source.** All files are `.md`. The numeric prefixes are the recommended order; you can drag them in as a batch. Skip `README.md` - that one is for you, not for NotebookLM.
3. Click **Slide Deck** in the Studio panel on the right.
4. In the **Customize Slide Deck** dialog, pick: **Format = Detailed Deck**, **Length = Default**, **Language = English**.
5. Open `00_PROMPTS.md` and copy the prompt block (between the triple backticks) into the **"Describe the slide deck you want to create"** field.
6. Click **Generate**.
7. If anything is off in the first draft, click **Customize** again and paste one of the follow-up tweaks listed at the bottom of `00_PROMPTS.md`.
8. When the deck is good, export from NotebookLM and apply your visual identity in PowerPoint or Google Slides.

NotebookLM grounds each output paragraph in the uploaded sources and shows the citation - that matches the integrity story this deck is selling, so keep all 16 files in the upload set.

## What each file is

| # | File | What it is |
|---|---|---|
| 00 | `00_PROMPTS.md` | The single description prompt to paste into NotebookLM's slide deck dialog, plus follow-up tweaks for iteration |
| 01 | `01_dossier_halyna.md` | The actual QA dossier the team wrote on the most recent Halyna run. Canonical "what a dossier looks like" reference. |
| 01 | `01_dossier_dorothy.md` | Dorothy F dossier - YELLOW with three agents flagging the same depth concern from different starting points (independence proof). |
| 01 | `01_dossier_jennifer.md` | Jennifer C dossier - YELLOW with only Customer Voice flagging a nuance. |
| 01 | `01_dossier_brittany.md` | Brittany W dossier - GREEN, all four agents agreed. |
| 02 | `02_verification_runs_ledger.md` | Audit trail of every persona replay - prior Goal ID, new Goal ID, what changed in the engine between them, date. The proof we preserve original customer-tested state forever. |
| 03 | `03_persona_corpus.md` | The regression contract. Every persona has expected_top5_includes, forbidden_in_top5, and a verbatim customer_quote. The file that grounds Customer Voice in real customer words. |
| 04 | `04_agent_team_overview.md` | The qa_agents package docstring describing all five agents. |
| 05 | `05_agent_customer_voice.md` | Customer Voice agent implementation - shows the prompt rules ("only customer_quote field is real, corpus fields are NOT quotes") and the severity sanity check. |
| 06 | `06_agent_skill_curator.md` | Skill Curator implementation - re-runs the rubric independently, compares against persona corpus. |
| 07 | `07_agent_path_coherence.md` | Path Coherence implementation - the deterministic DB invariants. |
| 08 | `08_agent_chapter_reviewer.md` | Chapter Reviewer implementation - identity check + LLM prose-fit. |
| 09 | `09_agent_demo_gate.md` | Demo Readiness Gate implementation + the dossier rendering. |
| 10 | `10_agent_orchestrator.md` | How the five agents run together (sequence, error handling, prior-verdict passing). |
| 11 | `11_rubric_scorer.md` | The 5-parameter weighted rubric (Importance x4 + Breadth x3 + Momentum x3 + Connectivity x2 + Career Signal x2 = 42 max). Includes role-essence floor + domain mandate + foundational PRM injection. |
| 12 | `12_sweep_integrity.md` | The deterministic DB-wide integrity sweep that runs alongside Path Coherence. |

## Folder location on your machine

```
c:\Users\ali_m\OneDrive\Business\Colaberry Novedea\AI Projects\AI Pathway Project\docs\notebooklm_deck_sources\
```

Or, opened in Explorer:

```
%USERPROFILE%\OneDrive\Business\Colaberry Novedea\AI Projects\AI Pathway Project\docs\notebooklm_deck_sources
```

## A few production notes

- **Do not** upload any other dossier, email, or DB dump unless it has been customer-cleared. The four dossiers here are the right grounding set; adding more dilutes the citations rather than strengthening them.
- The prompt in `00_PROMPTS.md` is written to NEVER use em dashes (your standing rule). If NotebookLM emits any in the generated deck, click Customize again and paste: "Replace every em dash with a hyphen surrounded by spaces, or a period."
- For the final visual pass, the in-product surfaces (ontology narrative panel, chapter disclosure, coach voice, summary page) use indigo / amber / emerald / navy. Asking NotebookLM to match those in the deck keeps the deck and the product visually aligned.
