# NotebookLM source pack - AI Pathway QA system enterprise deck

Everything you need to generate the enterprise slide deck on the multi-agent QA system. The files are numbered in the upload order that gives NotebookLM the strongest grounding.

## How to use this folder

1. Create a new NotebookLM notebook.
2. **Upload every file in this folder as a source.** All files are `.md` (NotebookLM accepts pdf / txt / md / docx / csv / pptx / epub plus media). The numeric prefixes are the recommended order; you can drag them in as a batch. Skip `README.md` - that one is for you, not for NotebookLM.
3. Open `00_PROMPTS.md` and copy the **System prompt** section into NotebookLM's Custom Instructions.
4. Copy the **Slide deck prompt** section into the main composer and run it.
5. Iterate: ask for tweaks per slide ("rewrite slide 3 with a simpler diagram description", "tighten slide 11 to under 80 words in speaker notes", etc.).
6. When the markdown outline is good, paste into PowerPoint (File > New > From Outline) or Google Slides (File > Import slides > Paste outline) and apply your visual identity.

NotebookLM grounds each output paragraph in the uploaded sources and shows the citation - that matches the integrity story this deck is selling, so keep all 16 files in the upload set.

## What each file is

| # | File | What it is | Used by slides |
|---|---|---|---|
| 00 | `00_PROMPTS.md` | The system prompt + the slide deck prompt | All |
| 01 | `01_dossier_halyna.md` | The actual QA dossier the team wrote on the most recent Halyna run. Use as the canonical "what a dossier looks like" reference. | 4, 5, 8, 11 |
| 01 | `01_dossier_dorothy.md` | Dorothy F dossier - confirmed YELLOW with three agents flagging the same depth concern from different starting points. | 9 (independence proof) |
| 01 | `01_dossier_jennifer.md` | Jennifer C dossier - YELLOW with only Customer Voice flagging a nuance. | 4 (Customer Voice example) |
| 01 | `01_dossier_brittany.md` | Brittany W dossier - GREEN, all four agents agreed. | 5 (Skill Curator example) |
| 02 | `02_verification_runs_ledger.md` | Audit trail of every persona replay - prior Goal ID, new Goal ID, what changed in the engine between them, date. The proof that we preserve original customer-tested state forever. | 12 (auditability) |
| 03 | `03_persona_corpus.md` | The regression contract. Every persona has expected_top5_includes, forbidden_in_top5, and a verbatim customer_quote. This is the file that grounds Customer Voice in real customer words. | 2, 4, 9 |
| 04 | `04_agent_team_overview.md` | The qa_agents package docstring describing all five agents. | 3 (the answer) |
| 05 | `05_agent_customer_voice.md` | Customer Voice agent implementation - shows the prompt rules ("only customer_quote field is real, corpus fields are NOT quotes") and the severity sanity check. | 4 |
| 06 | `06_agent_skill_curator.md` | Skill Curator implementation - re-runs the rubric independently, compares against persona corpus. | 5 |
| 07 | `07_agent_path_coherence.md` | Path Coherence implementation - the deterministic DB invariants. | 6 |
| 08 | `08_agent_chapter_reviewer.md` | Chapter Reviewer implementation - identity check + LLM prose-fit. | 7 |
| 09 | `09_agent_demo_gate.md` | Demo Readiness Gate implementation + the dossier rendering. | 8 |
| 10 | `10_agent_orchestrator.md` | How the five agents run together (sequence, error handling, prior-verdict passing). | 3, 9 |
| 11 | `11_rubric_scorer.md` | The 5-parameter weighted rubric (Importance x 4 + Breadth x 3 + Momentum x 3 + Connectivity x 2 + Career Signal x 2 = 42 max). Includes role-essence floor + domain mandate + foundational PRM injection. | 5, 10 |
| 12 | `12_sweep_integrity.md` | The deterministic DB-wide integrity sweep that runs alongside Path Coherence. | 6, 10 |

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
- The prompts in `00_PROMPTS.md` are written to NEVER use em dashes (your standing rule). If NotebookLM emits any in the generated outline, the most common fix is to add an explicit "use hyphens only, never em dashes" line to your composer prompt and re-run.
- For the final visual pass, the in-product surfaces (ontology narrative panel, chapter disclosure, coach voice, summary page) use indigo / amber / emerald / navy. Asking NotebookLM to match those in the deck keeps the deck and the product visually aligned.
