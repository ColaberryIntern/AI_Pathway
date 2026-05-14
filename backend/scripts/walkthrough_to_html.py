"""Generate the browsable HTML walkthrough with built-in feedback capture.

For each visual change, the HTML lets the client mark Approved / Issue / Question
and write notes. A floating "Generate Feedback Email" button compiles all
responses into a parseable email body that Claude Code can pick up and act on
directly.

The email body uses a magic header (ai-pathway-walkthrough-feedback-v1) and a
strict per-change format so a return reply can be parsed deterministically:
each change becomes either an APPROVED line or a NEEDS-CHANGE / QUESTION
block with its files, URL, and the client's notes.
"""
import base64
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path(__file__).parent.parent.parent / "docs" / "walkthrough_report"

# Keep this list as the single source of truth. walkthrough_report.py also
# uses these IDs when capturing screenshots.
CHANGES = [
    {"id": "01_homepage_simplified", "title": "Homepage simplified", "category": "Luda Apr 15", "page_url": "/",
     "what": "Removed 'How It Works' section and 'Ready to start your AI learning journey?' CTA block.",
     "why": "Per Luda Apr 15: page should fit on a single screen.",
     "files": ["frontend/src/pages/HomePage.tsx"], "to_see": "Open the URL above."},
    {"id": "02_profiles_copy", "title": "Profiles page copy update", "category": "Luda Apr 15", "page_url": "/profiles",
     "what": "Subhead changed from 'Create and manage learner profiles' to 'Create profiles for different career goals'.",
     "why": "Per Luda Apr 15: language tailored for individuals creating multiple profiles for themselves.",
     "files": ["frontend/src/pages/ProfileSelectionPage.tsx"], "to_see": "Open the URL above."},
    {"id": "03_skills_review_merged", "title": "Skill selection + self-assessment merged", "category": "Luda Apr 15", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "Combined two previously separate pages (skill selection, then self-assessment) into one unified page. When a skill is selected, the proficiency rating appears inline below it.",
     "why": "Per Luda Apr 15: reduce step count and let user adjust skills + ratings in one view.",
     "files": ["frontend/src/pages/AnalysisPage.tsx", "frontend/src/components/SelfAssessment.tsx"], "to_see": "Open the URL above."},
    {"id": "04_skill_hover_tooltip", "title": "Hover tooltip with ontology description on skill name", "category": "Vivek Apr 29 (NEW)", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "Skill names now have a dotted underline + cursor:help. Hovering shows the canonical ontology description and skill_id in a dark tooltip.",
     "why": "Per Vivek Apr 29 (confirmed Agreed): users shouldn't have to guess what a skill means. Show the authoritative ontology definition on hover.",
     "files": ["frontend/src/components/SelfAssessment.tsx", "frontend/src/pages/AnalysisPage.tsx"], "to_see": "Open URL, then hover over any skill name."},
    {"id": "05_targeted_role_label", "title": "Detected Role -> Targeted Role rename", "category": "Luda Apr 15", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "Label 'Detected role' renamed to 'Targeted role' throughout the tool.",
     "why": "Per Luda Apr 15: 'Targeted' is more accurate - the user is selecting a target, not having a role 'detected'.",
     "files": ["frontend/src/components/profile/TargetGoalPanel.tsx"], "to_see": "Open URL above."},
    {"id": "06_skill_match_messaging", "title": "End-of-page messaging when skills match target", "category": "Luda Apr 28", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "Changed messaging from 'we will proceed with the remaining X skills' to 'we will add other relevant skills to build a learning path consisting of 5 chapters'.",
     "why": "Per Luda Apr 28: clarify that the system backfills with new skills rather than just dropping the matched ones.",
     "files": ["frontend/src/pages/AnalysisPage.tsx"], "to_see": "Open URL, rate at least one skill at its target level."},
    {"id": "07_learning_dashboard_no_gate", "title": "Learning dashboard auto-activates (no Ready to Start gate)", "category": "Luda Apr 28", "page_url": "/learn/{path_id}",
     "what": "Removed 'Ready to Start Learning?' confirmation page that previously appeared between skill review and the dashboard. Path now auto-activates on load.",
     "why": "Per Luda Apr 28: the gate page was duplicative of the skill review confirmation.",
     "files": ["frontend/src/pages/LearningDashboardPage.tsx"], "to_see": "Open URL above."},
    {"id": "08_journey_roadmap_removed", "title": "Your Journey Roadmap page removed", "category": "Luda Apr 28", "page_url": "/analysis/{pid}",
     "what": "Removed the entire 'Your Journey Roadmap' page that previously appeared between skill review and the learning dashboard.",
     "why": "Per Luda Apr 28: the roadmap page was duplicative - same info already shown on the skill review page.",
     "files": ["frontend/src/pages/AnalysisPage.tsx"], "to_see": "Open URL above and click Continue to Learning Path - goes directly to dashboard."},
    {"id": "09_chapter_section_nav", "title": "Chapter section navigation (6 sections, 15 min)", "category": "Vivek + User Apr 30", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Chapter renderer shows 6 section tabs at top: Scenario (2m), Concepts (3m), Example 1 (3m), Example 2 (4m), Build (3m), Assignment (30m). The Assignment tab is the new 6th section.",
     "why": "Per Vivek's chapter spec (5 sections totaling 15 min) + user's Apr 30 request to bring back the Implementation Task assignment workflow.",
     "files": ["frontend/src/components/chapter/ChapterRenderer.tsx", "backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md"], "to_see": "Open URL above."},
    {"id": "10_chapter_title_ontology_name", "title": "Chapter title uses ontology canonical name", "category": "Vivek Apr 29 (NEW)", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Chapter title now displays the ontology canonical skill name (e.g. 'Prompt debugging & iteration') instead of the LLM-generated story title (e.g. 'Iterating on Prompts: From Literacy to Practitioner').",
     "why": "Per Vivek Apr 29 (confirmed Agreed) on Luda's request: skills should be named consistently using ontology names throughout the tool.",
     "files": ["frontend/src/components/chapter/ChapterRenderer.tsx"], "to_see": "Open URL above."},
    {"id": "11_concepts_with_mnemonic", "title": "Concepts section with mnemonic + pull_quote", "category": "Vivek depth fix", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Concepts section now requires a mnemonic field (e.g. 'IVL'), a pull_quote (single memorable sentence), and 2-4 concept cards each with identifier, word, headline, body, analogy, color_role.",
     "why": "Per Vivek's depth spec: chapters lacked structural depth. Mnemonic + pull_quote help retention.",
     "files": ["backend/app/data/chapter-generator-prompt.md", "backend/app/agents/chapter_generator.py"], "to_see": "Open URL above, click Concepts tab."},
    {"id": "12_example1_steps_array", "title": "Example 1 with 3-step structure (diagnosis_checklist / prompt_variant / log_entry)", "category": "Vivek depth fix", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Example 1 now requires a steps array with EXACTLY 3 entries: (1) diagnosis_checklist with broken/clear status flags, (2) prompt_variant ref, (3) log_entry table with key/value pairs.",
     "why": "Per Vivek's spec: Example 1 should walk learner through the diagnostic process, not just show a prompt and result.",
     "files": ["backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md", "frontend/src/components/chapter/ChapterRenderer.tsx"], "to_see": "Open URL above, click Example 1 tab."},
    {"id": "13_example2_ab_comparison", "title": "Example 2 A/B comparison", "category": "Vivek depth fix", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Example 2 must have a comparison object with test_question, exactly 2 variants (id A, id B) with full prompt/output/rating/why, and a takeaway.",
     "why": "Per Vivek's spec: Example 2 demonstrates the target-level skill (A/B testing) by example.",
     "files": ["backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md"], "to_see": "Open URL above, click Example 2 tab."},
    {"id": "14_agent_build_section", "title": "Build Your Agent section", "category": "Vivek spec", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Agent Build section requires: 3 capability_chips, 3 personalization_fields, system_prompt_template, usage_steps, and final_affirmation tying back to the rubric.",
     "why": "Per Vivek's spec: each chapter ends with a takeaway artifact the learner can use the same day.",
     "files": ["backend/app/agents/chapter_generator.py", "frontend/src/components/chapter/ChapterRenderer.tsx"], "to_see": "Open URL above, click Build tab."},
    {"id": "15_try_in_llm_buttons", "title": "Try-in-LLM buttons (Run in ChatGPT / Claude)", "category": "Vivek Apr 29 (NEW)", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Added 'Run in ChatGPT' / 'Run in Claude' buttons next to every prompt in the chapter: original_prompt, iterated_prompt, A/B variants, and the interpolated agent build template.",
     "why": "Per Vivek Apr 29: 'I also liked aspects of your previous build especially around giving links to try out the prompts in chatgpt or claude.'",
     "files": ["frontend/src/components/chapter/ChapterRenderer.tsx"], "to_see": "Open URL above, click Example 1 tab."},
    {"id": "16_implementation_task_section", "title": "Implementation Task as 6th section (NEW)", "category": "User Apr 30 (NEW)", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Brought back the Implementation Task assignment workflow as a 6th chapter section. Includes title, description, requirements, deliverable, tools, evidence_requirements (file uploads). Submit & Get Graded uses existing AI grading endpoint.",
     "why": "Per user's Apr 30 request: the assignment functionality from the old multi-lesson format was missing.",
     "files": ["backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md", "frontend/src/components/chapter/ChapterRenderer.tsx", "frontend/src/components/learning/ImplementationTaskCard.tsx"], "to_see": "Open URL above, click Assignment tab."},
    {"id": "17_deterministic_skill_ordering", "title": "Deterministic skill ordering between runs", "category": "Luda Apr 28", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "Set profile_analyzer LLM call to temperature=0. Verified across 20 consecutive runs - identical top 5 every time.",
     "why": "Per Luda Apr 28: she ran Jennifer C twice and got different top 5 skills.",
     "files": ["backend/app/agents/profile_analyzer.py"], "to_see": "Open URL above. Compare with another fresh run - same input gives same top 5."},
    {"id": "18_skill_rank_sequential", "title": "Skills render in sequential rank order (no duplicate or skipped numbers)", "category": "Luda May 9 (NEW)", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "Ranks #1..#N now sequential, in render order. Previously a single render could show duplicate #2 and skip #7, with the rank-1 skill rendering 5th. Backend normalizes ranks after JD parsing and after rerank/enrich; frontend defensively renumbers on revisit.",
     "why": "Per Luda May 9: 'the #1 skill (draft -> critique -> revise) appears at the end of the top 5' plus two #2s and no #7.",
     "files": ["backend/app/agents/jd_parser.py", "backend/app/api/routes/analysis.py", "frontend/src/pages/AnalysisPage.tsx"], "to_see": "Open URL above. Top of page shows skill cards labeled #1, #2, #3... in render order, no gaps or duplicates."},
    {"id": "19_dashboard_back_to_skill_review", "title": "Back to skill review link on the Learning Dashboard", "category": "Luda May 9 (NEW)", "page_url": "/learn/{path_id}",
     "what": "Learning Dashboard header now has a Back to skill review link that routes to /analysis/{profile_id}?view=skill_selection. Backend dashboard endpoint exposes profile_id; frontend renders the link when present.",
     "why": "Per Luda May 9: 'After I progress from that page to the AI Learning Path Dashboard, I cannot come back to the full list.'",
     "files": ["backend/app/schemas/learning.py", "backend/app/api/routes/learning.py", "frontend/src/types/index.ts", "frontend/src/pages/LearningDashboardPage.tsx"], "to_see": "Open URL above. Top-left of header has 'Back to skill review' link."},
    {"id": "20_rating_persistence", "title": "Proficiency ratings persist across navigation (no more 0/5 assessed reset)", "category": "Luda May 9 (NEW)", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "selfAssessedSkills state now reads from and writes to localStorage keyed by profileId. Navigating to /learn and back no longer resets the counter to 0/5.",
     "why": "Per Luda May 9 PDF: rated 5 skills but the next visit showed 0/5 assessed.",
     "files": ["frontend/src/pages/AnalysisPage.tsx"], "to_see": "Rate a few skills, navigate to the learning dashboard, come back. The counter still shows your prior ratings (not reset to 0)."},
    {"id": "21_per_skill_hover_descriptions", "title": "Hover tooltip shows per-skill, per-level rubric (not generic 'Can explain basics')", "category": "Vivek May 9 (NEW)", "page_url": "/analysis/{pid}?view=skill_selection",
     "what": "Ontology service now reads rubric_by_level (populated for every skill) and converts it to the proficiency_descriptions structure the frontend expects. Each level now has a skill-specific rubric instead of a generic scale line.",
     "why": "Per Vivek May 9 (item 04) and Luda Apr 29: wanted per-skill, per-level descriptions matching the ai-fluency-assessment ontology, not a generic 'Aware: Can explain basics' that's the same for every skill.",
     "files": ["backend/app/services/ontology.py"], "to_see": "Open URL above, hover any of the proficiency level buttons (0 Unaware, 1 Aware, 2 User, 3 Practitioner, 4 Builder) on any skill card. The tooltip shows that skill's specific rubric for that level. Example: SK.PRM.003 L1 shows 'Knows that prompts can be revised when output is unsatisfactory'."},
    {"id": "22_item_06_status_deferred", "title": "STATUS - Item 06 (interstitial proficiency-rating step) is deferred", "category": "Status Update (May 12)", "page_url": "/analysis/{pid}?view=skill_selection", "screenshot_id": "06_skill_match_messaging",
     "what": "The MESSAGE change you approved (\"build a learning path consisting of 5 chapters\") is shipping as-is. The separate request - inserting an interstitial page where the user rates the SWAPPED-IN skills (6, 7, 8) before chapter generation - is a new product requirement and is deferred per Luda's note that #6 can come after the demo round. Spec is captured at docs/follow_ups/06_interstitial_skill_rating.md in the repo.",
     "why": "Per Luda May 7 walkthrough feedback (item 06) and Luda's clarifying note: this can wait until after Jennifer demo.",
     "files": ["docs/follow_ups/06_interstitial_skill_rating.md (spec only)"], "to_see": "No code change to verify. Use this card's feedback widget if you want to revise priority (move to next round, change scope, etc.)."},
    {"id": "23_item_14_status_queued", "title": "STATUS - Item 14 (Build Your Agent fields) - Vivek's ask understood, queued", "category": "Status Update (May 12)", "page_url": "/learn/{path_id}/lesson/{lesson_id}", "screenshot_id": "14_agent_build_section", "click_tab": "Build",
     "what": "Vivek asked for the standard agent platform field set - description, instructions, knowledge base - mirroring what users see in ChatGPT custom GPTs, Copilot agents, and Gemini Gems. Currently the chapter generator emits 3 capability_chips + 3 personalization_fields + a system_prompt_template. Switching to description/instructions/knowledge base needs prompt + schema + renderer changes. Estimate ~1 hour. Queued for next chapter-format round.",
     "why": "Per Vivek May 9 walkthrough feedback (item 14): align the agent build UI with industry-standard agent-builder field sets.",
     "files": ["backend/app/agents/chapter_generator.py (planned)", "backend/app/data/chapter-generator-prompt.md (planned)", "frontend/src/components/chapter/ChapterRenderer.tsx (planned)"], "to_see": "No code change yet. Use this card's feedback widget to confirm the planned field set (description, instructions, knowledge base) is right, or flag a different structure."},
    {"id": "24_item_17_status_needs_clarification", "title": "STATUS - Item 17 (deterministic ordering) - need clarifying note from Vivek", "category": "Status Update (May 12)", "page_url": "/analysis/{pid}?view=skill_selection", "screenshot_id": "17_deterministic_skill_ordering",
     "what": "Vivek marked this Issue but left the comment empty. The change set profile_analyzer LLM call to temperature=0 so identical inputs produce identical top 5 across runs. Verified across 20 consecutive runs - same top 5 every time. Unable to act on the Issue without knowing the actual concern.",
     "why": "Per Vivek May 9 walkthrough feedback (item 17): status = Issue, feedback = (empty).",
     "files": ["backend/app/agents/profile_analyzer.py"], "to_see": "Vivek - please use this card's feedback widget to note the concern: is the determinism approach itself wrong, or is the resulting top 5 not what you expected for the JD?"},
]

CATEGORY_COLORS = {
    "Luda Apr 15": "#3b82f6",
    "Luda Apr 28": "#8b5cf6",
    "Vivek Apr 29 (NEW)": "#10b981",
    "Vivek depth fix": "#f59e0b",
    "Vivek spec": "#f59e0b",
    "Vivek + User Apr 30": "#10b981",
    "User Apr 30 (NEW)": "#ef4444",
    "Luda May 9 (NEW)": "#ec4899",
    "Vivek May 9 (NEW)": "#06b6d4",
    "Status Update (May 12)": "#6b7280",
}


def render_html():
    # WALKTHROUGH_FILTER_IDS env var lets us scope a single round of review
    # to only the items the reviewer hasn't seen yet, instead of replaying
    # the full history. Comma-separated CHANGES ids; empty/unset = all.
    import os as _os
    filter_raw = _os.environ.get("WALKTHROUGH_FILTER_IDS", "").strip()
    filter_ids = {s.strip() for s in filter_raw.split(",") if s.strip()} if filter_raw else None
    global CHANGES
    if filter_ids:
        CHANGES = [c for c in CHANGES if c["id"] in filter_ids]
        print(f"Filtered to {len(CHANGES)} items: {[c['id'] for c in CHANGES]}")
    md_path = REPORT_DIR / "WALKTHROUGH_REPORT.md"
    pid = path_id = lesson_id = ""
    if md_path.exists():
        text = md_path.read_text(encoding="utf-8")
        for line in text.split("\n"):
            if "Test profile created" in line:
                # Markdown wraps the UUID in backticks; fall back to whitespace
                # parsing for older reports that didn't.
                if "`" in line:
                    pid = line.split("`")[1]
                else:
                    cleaned = line.replace("**", "").split(":", 1)[1].strip()
                    pid = cleaned.split()[0] if cleaned else ""
            if "Test learning path:" in line:
                path_id = line.split("`")[1] if "`" in line else ""
            if "Test lesson:" in line:
                lesson_id = line.split("`")[1] if "`" in line else ""

    base = "http://95.216.199.47:3000"
    today = datetime.now().strftime("%B %d, %Y")
    iso_date = datetime.now().strftime("%Y-%m-%d")

    def url(template):
        return base + template.format(pid=pid, path_id=path_id, lesson_id=lesson_id)

    cards_html = []
    toc_items = []

    for i, c in enumerate(CHANGES, 1):
        color = CATEGORY_COLORS.get(c["category"], "#6b7280")
        full_url = url(c["page_url"])
        files_html = "".join(f"<li><code>{f}</code></li>" for f in c["files"])

        toc_items.append(
            f'<li data-id="{c["id"]}" data-category="{c["category"]}">'
            f'<a href="#change-{c["id"]}"><span class="num">{i}</span>{c["title"]}</a>'
            f'<span class="cat-pill" style="background:{color}">{c["category"]}</span>'
            f'<span class="status-dot" data-id="{c["id"]}"></span>'
            f'</li>'
        )

        # Embed the screenshot as a base64 data URI so the HTML is fully
        # self-contained. No external file dependencies; the reviewer just
        # opens the HTML and everything renders. Status-update cards reuse
        # an earlier round's screenshot via the screenshot_id field.
        screenshot_basename = c.get("screenshot_id") or c["id"]
        png_path = REPORT_DIR / "screenshots" / f"{screenshot_basename}.png"
        if png_path.exists():
            data_uri = (
                "data:image/png;base64,"
                + base64.b64encode(png_path.read_bytes()).decode("ascii")
            )
        else:
            data_uri = ""
        screenshot_html = (
            f'<a href="{data_uri}" target="_blank" class="shot">'
            f'<img src="{data_uri}" alt="{c["title"]}" loading="lazy">'
            f'<div class="zoom-hint">Click to enlarge</div></a>'
        )

        # Per-card feedback widget
        feedback_html = f'''
<div class="feedback" data-id="{c["id"]}" data-title="{c["title"].replace(chr(34), '&quot;')}" data-url="{full_url}" data-files="{','.join(c["files"])}">
    <div class="feedback-head">Your review:</div>
    <div class="feedback-radios">
        <label class="status-pill" data-status="approved">
            <input type="radio" name="status-{c["id"]}" value="approved">
            <span>Approved</span>
        </label>
        <label class="status-pill" data-status="issue">
            <input type="radio" name="status-{c["id"]}" value="issue">
            <span>Issue</span>
        </label>
        <label class="status-pill" data-status="question">
            <input type="radio" name="status-{c["id"]}" value="question">
            <span>Question</span>
        </label>
    </div>
    <textarea class="feedback-notes" placeholder="Notes (optional for Approved, required for Issue/Question)... e.g. 'Tooltip text is too small' or 'How does grading work?'"></textarea>
</div>
'''

        cards_html.append(f'''
<div class="card" id="change-{c["id"]}" data-category="{c["category"]}" data-search="{c["title"].lower()} {c["what"].lower()}">
    <div class="card-head">
        <span class="card-num">{i}</span>
        <h2>{c["title"]}</h2>
        <span class="cat-pill" style="background:{color}">{c["category"]}</span>
    </div>
    <div class="card-url">
        <span class="label">Live URL:</span>
        <a href="{full_url}" target="_blank" class="url">{full_url}</a>
        <button class="copy-btn" data-copy="{full_url}" title="Copy URL">copy</button>
    </div>
    <div class="card-tosee">
        <strong>To see this change:</strong> {c["to_see"]}
    </div>
    {screenshot_html}
    <div class="card-body">
        <div class="section">
            <h3>What was changed</h3>
            <p>{c["what"]}</p>
        </div>
        <div class="section">
            <h3>Why</h3>
            <p>{c["why"]}</p>
        </div>
        <div class="section">
            <h3>Files modified</h3>
            <ul>{files_html}</ul>
        </div>
        {feedback_html}
    </div>
</div>
''')

    cat_filter_buttons = "".join(
        f'<button class="cat-btn" data-cat="{cat}" style="border-color:{color}">{cat}</button>'
        for cat, color in CATEGORY_COLORS.items()
        if any(c["category"] == cat for c in CHANGES)
    )

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AI Pathway - Visual Changes Walkthrough</title>
<style>
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #f9fafb;
    color: #111827;
    line-height: 1.5;
}}
.layout {{ display: grid; grid-template-columns: 340px 1fr; min-height: 100vh; }}
.sidebar {{
    background: white;
    border-right: 1px solid #e5e7eb;
    padding: 20px;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
}}
.sidebar h1 {{ font-size: 18px; margin: 0 0 4px; }}
.sidebar .sub {{ font-size: 12px; color: #6b7280; margin-bottom: 16px; }}
.sidebar input[type=search] {{
    width: 100%;
    padding: 8px 10px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 13px;
    margin-bottom: 16px;
}}
.reviewer-block {{
    background: #fef9c3;
    border: 1px solid #fde047;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 16px;
}}
.reviewer-block label {{
    display: block;
    font-size: 13px;
    color: #1f2937;
    margin-bottom: 6px;
}}
.reviewer-block .req {{ color: #b91c1c; font-weight: 600; }}
.reviewer-block input[type=text] {{
    width: 100%;
    padding: 7px 9px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 13px;
    background: #fff;
}}
.reviewer-block input[type=text]:focus {{
    outline: none;
    border-color: #f59e0b;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
}}
.reviewer-block input[type=text].error {{
    border-color: #dc2626;
    background: #fef2f2;
}}
.reviewer-block .reviewer-hint {{
    font-size: 11px;
    color: #6b7280;
    margin-top: 4px;
}}
.progress-strip {{
    margin-bottom: 16px;
    padding: 10px 12px;
    background: linear-gradient(to right, #ecfdf5, #fef3c7);
    border: 1px solid #d1fae5;
    border-radius: 8px;
    font-size: 12px;
}}
.progress-strip strong {{ display: block; font-size: 14px; margin-bottom: 4px; }}
.progress-strip .counts {{ display: flex; gap: 12px; }}
.progress-strip .counts span {{ display: inline-flex; align-items: center; gap: 4px; }}
.dot {{
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
}}
.dot.approved {{ background: #10b981; }}
.dot.issue {{ background: #ef4444; }}
.dot.question {{ background: #f59e0b; }}
.dot.pending {{ background: #d1d5db; }}
.toc {{ list-style: none; padding: 0; margin: 0; }}
.toc li {{
    margin: 0;
    padding: 6px 0;
    border-top: 1px solid #f3f4f6;
    position: relative;
}}
.toc a {{
    text-decoration: none;
    color: #1f2937;
    font-size: 13px;
    display: block;
    padding: 4px 6px 4px 6px;
    padding-right: 24px;
    border-radius: 4px;
}}
.toc a:hover {{ background: #f3f4f6; }}
.toc .num {{
    display: inline-block;
    width: 24px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    background: #6366f1;
    color: white;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 8px;
}}
.toc .cat-pill {{
    display: inline-block;
    padding: 1px 6px;
    border-radius: 8px;
    font-size: 9px;
    color: white;
    margin-left: 32px;
    margin-top: 2px;
    font-weight: 500;
}}
.status-dot {{
    position: absolute;
    right: 6px;
    top: 12px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #d1d5db;
}}
.status-dot.approved {{ background: #10b981; }}
.status-dot.issue {{ background: #ef4444; }}
.status-dot.question {{ background: #f59e0b; }}
.main {{ padding: 32px 40px; max-width: 1100px; padding-bottom: 100px; }}
.page-head {{ margin-bottom: 32px; }}
.page-head h1 {{ font-size: 28px; margin: 0 0 8px; }}
.page-head .summary {{ color: #4b5563; font-size: 14px; }}
.page-head .summary strong {{ color: #111827; }}
.cat-filters {{ margin: 16px 0; display: flex; gap: 8px; flex-wrap: wrap; }}
.cat-btn {{
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    border: 1px solid #d1d5db;
    background: white;
    cursor: pointer;
    color: #4b5563;
}}
.cat-btn.active {{ background: #1f2937; color: white; border-color: #1f2937; }}

.card {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    margin-bottom: 32px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.card.has-issue {{ border-left: 4px solid #ef4444; }}
.card.has-question {{ border-left: 4px solid #f59e0b; }}
.card.has-approved {{ border-left: 4px solid #10b981; }}
.card-head {{
    padding: 16px 20px;
    background: linear-gradient(to bottom, #f9fafb, white);
    border-bottom: 1px solid #f3f4f6;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.card-num {{
    background: #1f2937;
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    flex-shrink: 0;
}}
.card-head h2 {{ font-size: 18px; margin: 0; flex: 1; }}
.cat-pill {{
    padding: 3px 10px;
    border-radius: 12px;
    color: white;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}}
.card-url {{
    padding: 12px 20px;
    background: #f3f4f6;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
}}
.card-url .label {{ font-weight: 600; color: #4b5563; }}
.card-url .url {{
    color: #2563eb;
    text-decoration: none;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    flex: 1;
    word-break: break-all;
}}
.card-url .url:hover {{ text-decoration: underline; }}
.copy-btn {{
    padding: 2px 8px;
    border: 1px solid #d1d5db;
    background: white;
    border-radius: 4px;
    font-size: 11px;
    cursor: pointer;
    color: #4b5563;
}}
.copy-btn:hover {{ background: #f3f4f6; }}
.copy-btn.copied {{ background: #10b981; color: white; border-color: #10b981; }}
.card-tosee {{
    padding: 10px 20px;
    background: #fef3c7;
    border-bottom: 1px solid #fde68a;
    font-size: 13px;
    color: #78350f;
}}
.shot {{
    display: block;
    background: #1f2937;
    text-align: center;
    position: relative;
    text-decoration: none;
}}
.shot img {{
    max-width: 100%;
    display: block;
    margin: 0 auto;
    cursor: zoom-in;
}}
.zoom-hint {{
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 11px;
    opacity: 0;
    transition: opacity 0.15s;
}}
.shot:hover .zoom-hint {{ opacity: 1; }}
.card-body {{ padding: 20px 24px; }}
.section {{ margin-bottom: 16px; }}
.section h3 {{
    margin: 0 0 6px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #6b7280;
    font-weight: 600;
}}
.section p {{ margin: 0; color: #1f2937; }}
.section ul {{ margin: 0; padding-left: 20px; }}
.section ul li {{ margin: 2px 0; }}
.section code {{
    background: #f3f4f6;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    color: #1e40af;
}}

.feedback {{
    margin-top: 20px;
    padding: 16px;
    background: #f9fafb;
    border: 1px dashed #d1d5db;
    border-radius: 8px;
}}
.feedback-head {{
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #6b7280;
    font-weight: 600;
    margin-bottom: 8px;
}}
.feedback-radios {{ display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; }}
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border: 1px solid #d1d5db;
    border-radius: 16px;
    font-size: 12px;
    cursor: pointer;
    background: white;
    user-select: none;
}}
.status-pill input {{ display: none; }}
.status-pill[data-status="approved"] {{ color: #065f46; }}
.status-pill[data-status="issue"] {{ color: #991b1b; }}
.status-pill[data-status="question"] {{ color: #92400e; }}
.status-pill.selected[data-status="approved"] {{ background: #d1fae5; border-color: #10b981; }}
.status-pill.selected[data-status="issue"] {{ background: #fee2e2; border-color: #ef4444; }}
.status-pill.selected[data-status="question"] {{ background: #fef3c7; border-color: #f59e0b; }}
.feedback-notes {{
    width: 100%;
    min-height: 60px;
    padding: 8px 10px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-family: inherit;
    font-size: 13px;
    resize: vertical;
}}
.card.hidden {{ display: none; }}

/* Floating action bar */
.fab {{
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #4f46e5;
    color: white;
    padding: 14px 24px;
    border: none;
    border-radius: 50px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.fab .badge {{
    background: white;
    color: #4f46e5;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
}}
.fab:hover {{ background: #4338ca; }}

/* Modal */
.modal-bg {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.6);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 2000;
}}
.modal-bg.show {{ display: flex; }}
.modal {{
    background: white;
    width: 800px;
    max-width: 95vw;
    max-height: 85vh;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}
.modal-head {{
    padding: 16px 20px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.modal-head h3 {{ margin: 0; font-size: 18px; flex: 1; }}
.modal-close {{
    background: none;
    border: none;
    cursor: pointer;
    font-size: 20px;
    color: #6b7280;
}}
.modal-body {{ padding: 16px 20px; overflow-y: auto; flex: 1; }}
.modal-body label {{
    display: block;
    margin-bottom: 8px;
    font-size: 13px;
    color: #4b5563;
}}
.modal-body input[type=text] {{
    width: 100%;
    padding: 8px 10px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 13px;
    margin-bottom: 12px;
}}
.email-preview {{
    width: 100%;
    min-height: 320px;
    max-height: 50vh;
    padding: 12px;
    background: #f9fafb;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    white-space: pre;
    overflow: auto;
    resize: vertical;
}}
.modal-foot {{
    padding: 14px 20px;
    border-top: 1px solid #e5e7eb;
    display: flex;
    gap: 8px;
    justify-content: flex-end;
}}
.btn {{
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid transparent;
}}
.btn-primary {{ background: #4f46e5; color: white; border-color: #4f46e5; }}
.btn-primary:hover {{ background: #4338ca; }}
.btn-secondary {{ background: white; color: #4b5563; border-color: #d1d5db; }}
.btn-secondary:hover {{ background: #f3f4f6; }}

@media (max-width: 900px) {{
    .layout {{ grid-template-columns: 1fr; }}
    .sidebar {{ position: static; height: auto; border-right: none; border-bottom: 1px solid #e5e7eb; }}
}}
</style>
</head>
<body>
<div class="layout">
    <aside class="sidebar">
        <h1>Visual Changes</h1>
        <div class="sub">{len(CHANGES)} changes - generated {today}</div>
        <div class="progress-strip">
            <strong>Your review progress: <span id="reviewed-count">0</span> / {len(CHANGES)}</strong>
            <div class="counts">
                <span><span class="dot approved"></span> <span id="cnt-approved">0</span> approved</span>
                <span><span class="dot issue"></span> <span id="cnt-issue">0</span> issue</span>
                <span><span class="dot question"></span> <span id="cnt-question">0</span> question</span>
                <span><span class="dot pending"></span> <span id="cnt-pending">{len(CHANGES)}</span> pending</span>
            </div>
        </div>
        <div class="reviewer-block">
            <label for="reviewer-name"><strong>Your name</strong> <span class="req">(required)</span></label>
            <input type="text" id="reviewer-name" placeholder="e.g. Luda Kopeikina" autocomplete="name">
            <div class="reviewer-hint">Used in your feedback email signature. Saved automatically.</div>
        </div>
        <input type="search" placeholder="Search changes..." id="search">
        <ul class="toc">
            {"".join(toc_items)}
        </ul>
    </aside>
    <main class="main">
        <div class="page-head">
            <h1>AI Pathway - Visual Changes Walkthrough</h1>
            <div class="summary">
                <strong>Generated:</strong> {today} &nbsp;|&nbsp;
                <strong>Tool URL:</strong> <a href="{base}/" target="_blank">{base}</a><br>
                Walk through {len(CHANGES)} visual changes. For each one, click the live URL to verify it in the tool,
                then mark <strong>Approved</strong>, <strong>Issue</strong>, or <strong>Question</strong> below the screenshot
                and add a note. When done, click the floating "Generate Feedback Email" button bottom-right
                to compile your feedback into a copy-paste-ready email.
            </div>
            <div class="cat-filters">
                <button class="cat-btn active" data-cat="all">All ({len(CHANGES)})</button>
                {cat_filter_buttons}
            </div>
        </div>
        {"".join(cards_html)}
    </main>
</div>

<button class="fab" id="generate-feedback">
    Generate Feedback Email <span class="badge" id="fab-count">0/{len(CHANGES)}</span>
</button>

<div class="modal-bg" id="modal-bg">
    <div class="modal">
        <div class="modal-head">
            <h3>Feedback email - copy and send to Ali</h3>
            <button class="modal-close" id="modal-close">&times;</button>
        </div>
        <div class="modal-body">
            <label>Email body (preformatted - just copy and paste):</label>
            <textarea class="email-preview" id="email-body" readonly></textarea>
        </div>
        <div class="modal-foot">
            <button class="btn btn-secondary" id="copy-email">Copy email body to clipboard</button>
            <button class="btn btn-primary" id="open-mail">Open in email client</button>
        </div>
    </div>
</div>

<script>
const REPORT_DATE = "{iso_date}";
const TOOL_URL = "{base}";
const CHANGES = {len(CHANGES)};

// LocalStorage key tied to this report so refreshes don't lose progress
const STORAGE_KEY = "ai-pathway-walkthrough-feedback-" + REPORT_DATE;

function saveState() {{
    const state = {{}};
    document.querySelectorAll('.feedback').forEach(fb => {{
        const id = fb.dataset.id;
        const status = fb.querySelector('input[type=radio]:checked')?.value || '';
        const notes = fb.querySelector('.feedback-notes').value || '';
        if (status || notes) state[id] = {{ status, notes }};
    }});
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    localStorage.setItem('ai-pathway-reviewer-name', document.getElementById('reviewer-name').value || '');
}}

function loadState() {{
    try {{
        const state = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}');
        Object.keys(state).forEach(id => {{
            const fb = document.querySelector(`.feedback[data-id="${{id}}"]`);
            if (!fb) return;
            const {{ status, notes }} = state[id];
            if (status) {{
                const radio = fb.querySelector(`input[value="${{status}}"]`);
                if (radio) {{
                    radio.checked = true;
                    radio.closest('.status-pill').classList.add('selected');
                    updateCardStyle(fb.closest('.card'), status);
                    updateStatusDot(id, status);
                }}
            }}
            if (notes) fb.querySelector('.feedback-notes').value = notes;
        }});
        const name = localStorage.getItem('ai-pathway-reviewer-name');
        if (name) document.getElementById('reviewer-name').value = name;
    }} catch (e) {{ console.error(e); }}
    updateCounts();
}}

function updateCardStyle(card, status) {{
    card.classList.remove('has-approved', 'has-issue', 'has-question');
    if (status) card.classList.add('has-' + status);
}}
function updateStatusDot(id, status) {{
    const dot = document.querySelector(`.status-dot[data-id="${{id}}"]`);
    if (!dot) return;
    dot.classList.remove('approved', 'issue', 'question');
    if (status) dot.classList.add(status);
}}

function updateCounts() {{
    let approved = 0, issue = 0, question = 0;
    document.querySelectorAll('.feedback').forEach(fb => {{
        const status = fb.querySelector('input[type=radio]:checked')?.value || '';
        if (status === 'approved') approved++;
        else if (status === 'issue') issue++;
        else if (status === 'question') question++;
    }});
    const reviewed = approved + issue + question;
    document.getElementById('reviewed-count').textContent = reviewed;
    document.getElementById('cnt-approved').textContent = approved;
    document.getElementById('cnt-issue').textContent = issue;
    document.getElementById('cnt-question').textContent = question;
    document.getElementById('cnt-pending').textContent = CHANGES - reviewed;
    document.getElementById('fab-count').textContent = reviewed + '/' + CHANGES;
}}

document.querySelectorAll('.feedback').forEach(fb => {{
    fb.querySelectorAll('input[type=radio]').forEach(radio => {{
        radio.addEventListener('change', () => {{
            fb.querySelectorAll('.status-pill').forEach(p => p.classList.remove('selected'));
            radio.closest('.status-pill').classList.add('selected');
            const status = radio.value;
            updateCardStyle(fb.closest('.card'), status);
            updateStatusDot(fb.dataset.id, status);
            saveState();
            updateCounts();
        }});
    }});
    fb.querySelector('.feedback-notes').addEventListener('input', () => {{ saveState(); }});
}});

// Search filter
const search = document.getElementById('search');
search.addEventListener('input', () => {{
    const q = search.value.toLowerCase().trim();
    document.querySelectorAll('.card').forEach(card => {{
        const text = card.dataset.search || '';
        card.classList.toggle('hidden', q && !text.includes(q));
    }});
    document.querySelectorAll('.toc li').forEach(li => {{
        const link = li.querySelector('a');
        if (!link) return;
        const target = document.querySelector(link.getAttribute('href'));
        li.style.display = (target && !target.classList.contains('hidden')) ? '' : 'none';
    }});
}});

document.querySelectorAll('.cat-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
        document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const cat = btn.dataset.cat;
        document.querySelectorAll('.card').forEach(card => {{
            card.classList.toggle('hidden', cat !== 'all' && card.dataset.category !== cat);
        }});
        document.querySelectorAll('.toc li').forEach(li => {{
            const link = li.querySelector('a');
            if (!link) return;
            const target = document.querySelector(link.getAttribute('href'));
            li.style.display = (target && !target.classList.contains('hidden')) ? '' : 'none';
        }});
    }});
}});

document.querySelectorAll('.copy-btn').forEach(btn => {{
    btn.addEventListener('click', async () => {{
        try {{
            await navigator.clipboard.writeText(btn.dataset.copy);
            btn.classList.add('copied');
            const orig = btn.textContent;
            btn.textContent = 'copied!';
            setTimeout(() => {{ btn.classList.remove('copied'); btn.textContent = orig; }}, 1500);
        }} catch (e) {{}}
    }});
}});

// Generate feedback email body
function buildEmailBody() {{
    const reviewer = document.getElementById('reviewer-name').value.trim() || '<your name>';
    const approved = [], issues = [], questions = [], pending = [];
    document.querySelectorAll('.feedback').forEach(fb => {{
        const id = fb.dataset.id;
        const title = fb.dataset.title;
        const url = fb.dataset.url;
        const files = fb.dataset.files;
        const status = fb.querySelector('input[type=radio]:checked')?.value || '';
        const notes = (fb.querySelector('.feedback-notes').value || '').trim();
        const entry = {{ id, title, url, files, notes }};
        if (status === 'approved') approved.push(entry);
        else if (status === 'issue') issues.push(entry);
        else if (status === 'question') questions.push(entry);
        else pending.push(entry);
    }});

    const lines = [];
    lines.push('[ai-pathway-walkthrough-feedback-v1]');
    lines.push('Report-Date: ' + REPORT_DATE);
    lines.push('Reviewer: ' + reviewer);
    lines.push('Total: ' + CHANGES + ' | Approved: ' + approved.length + ' | Issues: ' + issues.length + ' | Questions: ' + questions.length + ' | Pending: ' + pending.length);
    lines.push('');
    lines.push('=== APPROVED (' + approved.length + ') ===');
    if (approved.length === 0) {{
        lines.push('(none)');
    }} else {{
        approved.forEach(e => {{
            lines.push('- [' + e.id + '] ' + e.title + (e.notes ? ' -- ' + e.notes : ''));
        }});
    }}
    lines.push('');
    lines.push('=== NEEDS CHANGE (' + issues.length + ') ===');
    if (issues.length === 0) {{
        lines.push('(none)');
    }} else {{
        issues.forEach(e => {{
            lines.push('');
            lines.push('### ' + e.id);
            lines.push('Title: ' + e.title);
            lines.push('URL: ' + e.url);
            lines.push('Files: ' + e.files);
            lines.push('Feedback: ' + (e.notes || '(no notes provided)'));
        }});
    }}
    lines.push('');
    lines.push('=== QUESTIONS (' + questions.length + ') ===');
    if (questions.length === 0) {{
        lines.push('(none)');
    }} else {{
        questions.forEach(e => {{
            lines.push('');
            lines.push('### ' + e.id);
            lines.push('Title: ' + e.title);
            lines.push('URL: ' + e.url);
            lines.push('Question: ' + (e.notes || '(no notes provided)'));
        }});
    }}
    if (pending.length > 0) {{
        lines.push('');
        lines.push('=== NOT YET REVIEWED (' + pending.length + ') ===');
        pending.forEach(e => {{ lines.push('- [' + e.id + '] ' + e.title); }});
    }}
    lines.push('');
    lines.push('[end-feedback]');
    lines.push('');
    lines.push('---');
    lines.push('Thanks,');
    lines.push(reviewer);
    return lines.join('\\n');
}}

const modalBg = document.getElementById('modal-bg');
document.getElementById('generate-feedback').addEventListener('click', () => {{
    const nameInput = document.getElementById('reviewer-name');
    if (!nameInput.value.trim()) {{
        nameInput.classList.add('error');
        nameInput.focus();
        nameInput.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        alert('Please fill in your name in the highlighted yellow box at the top of the left sidebar, then click Generate Feedback Email again.');
        return;
    }}
    nameInput.classList.remove('error');
    document.getElementById('email-body').value = buildEmailBody();
    modalBg.classList.add('show');
}});
document.getElementById('modal-close').addEventListener('click', () => modalBg.classList.remove('show'));
modalBg.addEventListener('click', (e) => {{ if (e.target === modalBg) modalBg.classList.remove('show'); }});
document.getElementById('reviewer-name').addEventListener('input', () => {{
    saveState();
    document.getElementById('email-body').value = buildEmailBody();
}});
document.getElementById('copy-email').addEventListener('click', async (e) => {{
    try {{
        await navigator.clipboard.writeText(document.getElementById('email-body').value);
        e.target.textContent = 'copied!';
        setTimeout(() => {{ e.target.textContent = 'Copy email body to clipboard'; }}, 2000);
    }} catch (err) {{}}
}});
document.getElementById('open-mail').addEventListener('click', () => {{
    const subject = encodeURIComponent('AI Pathway walkthrough feedback - ' + REPORT_DATE);
    const body = encodeURIComponent(document.getElementById('email-body').value);
    window.location.href = 'mailto:ali@colaberry.com?subject=' + subject + '&body=' + body;
}});

loadState();
</script>
</body>
</html>
'''

    out = REPORT_DIR / "WALKTHROUGH.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote: {out}")
    print(f"Open in browser: file:///{str(out).replace(chr(92), '/')}")


if __name__ == "__main__":
    render_html()
