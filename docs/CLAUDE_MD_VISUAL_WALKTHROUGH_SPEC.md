# Visual-Changes Walkthrough Workflow

**Purpose:** Whenever the team ships visual/UX changes to the AI Pathway tool, produce a single self-contained HTML file the client (Luda, Vivek, Ram) can walk through, mark up, and email back. Their reply is structured so that Claude Code can parse it and start the next round of fixes immediately.

**Add this entire section to `CLAUDE.md` so any future Claude session shipping visual work follows the same pattern.**

---

## When to run the walkthrough workflow

Run this AFTER every batch of visual or UX changes — including:

- New pages, new sections, removed sections, removed pages
- Copy changes, button label changes, form layout changes
- New components, new modals, new tooltips
- Style changes that affect what the user sees (colors, spacing, hover states)
- Any change that a non-technical reviewer would notice by clicking around

Do NOT run for: backend-only changes, schema changes with no UI surface, infrastructure work, log/telemetry changes.

A change qualifies if a screenshot can show "before" vs "after."

## The two-script pipeline

### Script 1: `backend/scripts/walkthrough_report.py`

Captures the screenshots with red highlights around each changed element.

**What it does, in order:**
1. Creates a fresh test profile via the API (uses Jennifer C as the canonical test persona)
2. Runs the analysis pipeline end-to-end
3. Activates the learning path
4. Generates the first chapter (so the chapter view has real content to screenshot)
5. For each entry in its `CHANGES` list:
   - Navigates to the page URL
   - Optionally clicks a tab (`click_tab` field) or hovers an element (`hover_first` field)
   - Injects JavaScript that draws a red rectangle around the affected element + a red label box above it
   - Takes a viewport screenshot
   - Clears the highlight before the next iteration
6. Cleans up the test profile
7. Writes a markdown summary

**Key fields per change:**
- `id`: stable identifier like `04_skill_hover_tooltip` — used as filename and email key
- `title`: short human-readable name
- `category`: one of `Luda Apr 28`, `Vivek Apr 29 (NEW)`, `User Apr 30 (NEW)`, etc. — color-coded in the HTML
- `page_url`: relative URL (uses `{pid}`, `{path_id}`, `{lesson_id}` placeholders)
- `highlight_selector` OR `highlight_text`: how to find the element to highlight
- `highlight_label`: text shown in the red label box
- `what_changed`: the change description
- `why_changed`: reference to the request/feedback that prompted it
- `files_modified`: list of files Claude touched (PARSED LATER for fix-routing)
- `click_tab` / `hover_first`: optional flags to set up the right page state

### Script 2: `backend/scripts/walkthrough_to_html.py`

Reads the same `CHANGES` list and renders a single self-contained `WALKTHROUGH.html`.

**Required HTML features (any reimplementation must preserve all of these):**

1. **Sticky left sidebar** with:
   - Numbered table of contents (each item links to its card)
   - Color-coded category pill per item
   - Status dot per item that updates as the reviewer marks Approved/Issue/Question
   - Live progress strip showing approved/issue/question/pending counts
   - Search box that filters cards live

2. **Category filter pills** at the top of the main column

3. **One card per change** with:
   - Numbered header + title + category pill
   - Live URL with copy-to-clipboard button
   - Yellow "To see this change" instruction strip
   - Full screenshot (click to open at full resolution in new tab)
   - "What was changed" / "Why" / "Files modified" sections

4. **Per-card feedback widget** (CRITICAL — this is what makes the workflow work):
   - Three radio buttons: Approved / Issue / Question
   - Notes textarea (required for Issue/Question, optional for Approved)
   - Selecting a status colors the card's left border (green/red/amber)
   - Notes auto-saved to localStorage so refresh doesn't lose progress

5. **Floating "Generate Feedback Email" button** bottom-right with live count of reviewed-vs-total

6. **Modal that compiles all feedback into a parseable email body** — see "Email format contract" below

7. **mailto: handoff** that pre-fills `ali@colaberry.com` with the subject line `AI Pathway walkthrough feedback - <YYYY-MM-DD>` and the body

## Email format contract (DO NOT CHANGE LIGHTLY)

The HTML produces an email body with a strict format so Claude Code can parse it deterministically. Any future change to this format MUST be coordinated — the parser on the Claude Code side reads these markers literally.

```
[ai-pathway-walkthrough-feedback-v1]
Report-Date: 2026-05-05
Reviewer: Luda Kopeikina
Total: 17 | Approved: 12 | Issues: 3 | Questions: 2 | Pending: 0

=== APPROVED (12) ===
- [01_homepage_simplified] Homepage simplified
- [02_profiles_copy] Profiles page copy update
- [03_skills_review_merged] Skill selection + self-assessment merged -- nice change
... (one line per approved item)

=== NEEDS CHANGE (3) ===

### 04_skill_hover_tooltip
Title: Hover tooltip with ontology description on skill name
URL: http://95.216.199.47:3000/analysis/abc-123
Files: frontend/src/components/SelfAssessment.tsx,frontend/src/pages/AnalysisPage.tsx
Feedback: Tooltip text is too small, please make it bigger and use a lighter background.

### 10_chapter_title_ontology_name
Title: Chapter title uses ontology canonical name
URL: http://95.216.199.47:3000/learn/path-id/lesson/lesson-id
Files: frontend/src/components/chapter/ChapterRenderer.tsx
Feedback: I actually preferred the story-style title. Can we show both?

=== QUESTIONS (2) ===

### 16_implementation_task_section
Title: Implementation Task as 6th section (NEW)
URL: http://95.216.199.47:3000/learn/path-id/lesson/lesson-id
Question: How does the AI grading score actually work? What's the rubric?

[end-feedback]

---
Thanks,
Luda Kopeikina
```

**Format invariants:**
- The opening marker `[ai-pathway-walkthrough-feedback-v1]` is the version pin. Bump the `v1` if the format changes incompatibly.
- The closing marker `[end-feedback]` lets the parser ignore signature lines.
- Every NEEDS CHANGE / QUESTION block uses `### <change-id>` as its header. The `<change-id>` matches the `id` field in `walkthrough_to_html.py`'s CHANGES list.
- Each block has `Title:`, `URL:`, `Files:`, and either `Feedback:` (issue) or `Question:` (question). The `Files:` line is comma-separated.
- APPROVED entries are single lines: `- [<change-id>] <title> -- <optional notes>` (notes after the `--` separator).
- The `Total: ... | Approved: N | Issues: N | Questions: N | Pending: N` summary line is parseable by Claude Code with a simple regex.

## When the client emails their feedback back

When you (Claude) receive an email from Luda, Vivek, or Ram that contains the marker `[ai-pathway-walkthrough-feedback-v1]`:

1. **Parse the body** to extract three lists: approved, issues, questions.
2. **For each ISSUE block:**
   - The `Files:` line tells you exactly which files to start in.
   - The `Feedback:` line tells you what to change.
   - Open the files, make the change.
3. **For each QUESTION block:**
   - Draft an answer (don't make code changes for questions unless the answer requires one).
   - Include the question and your answer in the reply email.
4. **For APPROVED items:** no action needed beyond acknowledging in the reply.
5. **Re-run the walkthrough scripts after fixing** so the next round has fresh screenshots reflecting the new state.
6. **Reply with a confirmation email** listing what was fixed (and which approved items shipped unchanged) so the reviewer knows what to re-test.

## How to keep the CHANGES list in sync

Both scripts read from the same `CHANGES` list — but `walkthrough_report.py` has the canonical list (it's the one that captures screenshots). `walkthrough_to_html.py` mirrors the structure with a few additional metadata fields.

When you add a new visual change:

1. Add an entry to the `CHANGES` list in `walkthrough_report.py` with the screenshot-capture fields
2. Mirror the entry in `walkthrough_to_html.py` with the same `id` plus the metadata fields
3. Run `walkthrough_report.py` (creates fresh screenshots)
4. Run `walkthrough_to_html.py` (rebuilds the HTML)
5. Send the resulting `docs/walkthrough_report/WALKTHROUGH.html` and screenshots to the client

## File outputs

After running both scripts, you should have:

```
docs/walkthrough_report/
├── WALKTHROUGH.html           # Main client-facing file (open in browser)
├── WALKTHROUGH_REPORT.md      # Markdown fallback
├── 01_homepage_simplified.png  # One screenshot per change
├── 02_profiles_copy.png
├── 03_skills_review_merged.png
└── ... (one .png per CHANGES entry, named by id)
```

The HTML file references the screenshots by relative path, so the entire `docs/walkthrough_report/` directory must travel together (zip it before emailing, or host it).

## One-command to regenerate everything

```bash
cd backend
py -3.12 scripts/walkthrough_report.py    # captures screenshots (~3 min, hits the live API)
py -3.12 scripts/walkthrough_to_html.py    # rebuilds HTML from the screenshots (~1 sec)
start docs/walkthrough_report/WALKTHROUGH.html   # opens in default browser
```

## Why this workflow

- **Client doesn't need to install anything.** Open the HTML, click around, type notes, hit "Generate Feedback Email."
- **Notes are auto-saved.** Refreshing the browser doesn't lose work.
- **Feedback is structured.** Claude Code reads the email and knows immediately which files to open, which lines need changing, and what the request is.
- **Round-trip is fast.** Ship change -> generate report -> client reviews + emails -> Claude parses + fixes -> ship next round. No more "what did you mean exactly?" back-and-forth.
- **Each item is independently auditable.** Approved items don't get re-tested. Only issues + questions need attention next round.
