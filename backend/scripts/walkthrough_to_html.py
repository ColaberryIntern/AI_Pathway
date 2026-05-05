"""Convert the walkthrough_report.json data into a rich, browsable HTML page.

Reads the markdown report (or regenerates from scratch) and produces
a single self-contained HTML file with:
- Sticky sidebar table of contents
- Each change in a card with full-size screenshot (click to zoom)
- Filter/search box
- Copy-to-clipboard for URLs
- Color-coded categories (Luda fix, Vivek fix, NEW)
"""
import json
from pathlib import Path

REPORT_DIR = Path(__file__).parent.parent.parent / "docs" / "walkthrough_report"

# Re-define the changes here so we can add metadata (category, etc.) without
# parsing the markdown. Keep in sync with walkthrough_report.py.
CHANGES = [
    {"id": "01_homepage_simplified", "title": "Homepage simplified", "category": "Luda Apr 15", "page_url": "/",
     "what": "Removed 'How It Works' section and 'Ready to start your AI learning journey?' CTA block.",
     "why": "Per Luda Apr 15: page should fit on a single screen.",
     "files": ["frontend/src/pages/HomePage.tsx"], "to_see": "Open the URL above."},
    {"id": "02_profiles_copy", "title": "Profiles page copy update", "category": "Luda Apr 15", "page_url": "/profiles",
     "what": "Subhead changed from 'Create and manage learner profiles' to 'Create profiles for different career goals'.",
     "why": "Per Luda Apr 15: language tailored for individuals creating multiple profiles for themselves.",
     "files": ["frontend/src/pages/ProfileSelectionPage.tsx"], "to_see": "Open the URL above."},
    {"id": "03_skills_review_merged", "title": "Skill selection + self-assessment merged", "category": "Luda Apr 15", "page_url": "/analysis/{pid}",
     "what": "Combined two previously separate pages (skill selection, then self-assessment) into one unified page. When a skill is selected, the proficiency rating appears inline below it.",
     "why": "Per Luda Apr 15: reduce step count and let user adjust skills + ratings in one view.",
     "files": ["frontend/src/pages/AnalysisPage.tsx", "frontend/src/components/SelfAssessment.tsx"], "to_see": "Open the URL above."},
    {"id": "04_skill_hover_tooltip", "title": "Hover tooltip with ontology description on skill name", "category": "Vivek Apr 29 (NEW today)", "page_url": "/analysis/{pid}",
     "what": "Skill names now have a dotted underline + cursor:help. Hovering shows the canonical ontology description and skill_id in a dark tooltip.",
     "why": "Per Vivek Apr 29 (confirmed Agreed): users shouldn't have to guess what a skill means. Show the authoritative ontology definition on hover.",
     "files": ["frontend/src/components/SelfAssessment.tsx", "frontend/src/pages/AnalysisPage.tsx"], "to_see": "Open URL, then hover over any skill name."},
    {"id": "05_targeted_role_label", "title": "Detected Role -> Targeted Role rename", "category": "Luda Apr 15", "page_url": "/analysis/{pid}",
     "what": "Label 'Detected role' renamed to 'Targeted role' throughout the tool.",
     "why": "Per Luda Apr 15: 'Targeted' is more accurate - the user is selecting a target, not having a role 'detected'.",
     "files": ["frontend/src/components/profile/TargetGoalPanel.tsx"], "to_see": "Open URL above."},
    {"id": "06_skill_match_messaging", "title": "End-of-page messaging when skills match target", "category": "Luda Apr 28", "page_url": "/analysis/{pid}",
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
    {"id": "09_chapter_section_nav", "title": "Chapter section navigation (6 sections, 15 min)", "category": "Vivek + Apr 30", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
     "what": "Chapter renderer shows 6 section tabs at top: Scenario (2m), Concepts (3m), Example 1 (3m), Example 2 (4m), Build (3m), Assignment (30m). The Assignment tab is the new 6th section.",
     "why": "Per Vivek's chapter spec (5 sections totaling 15 min) + user's request to bring back the Implementation Task assignment workflow.",
     "files": ["frontend/src/components/chapter/ChapterRenderer.tsx", "backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md"], "to_see": "Open URL above."},
    {"id": "10_chapter_title_ontology_name", "title": "Chapter title uses ontology canonical name", "category": "Vivek Apr 29 (NEW today)", "page_url": "/learn/{path_id}/lesson/{lesson_id}",
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
    {"id": "17_deterministic_skill_ordering", "title": "Deterministic skill ordering between runs", "category": "Luda Apr 28", "page_url": "/analysis/{pid}",
     "what": "Set profile_analyzer LLM call to temperature=0. Verified across 20 consecutive runs - identical top 5 every time.",
     "why": "Per Luda Apr 28: she ran Jennifer C twice and got different top 5 skills.",
     "files": ["backend/app/agents/profile_analyzer.py"], "to_see": "Open URL above. Compare with another fresh run - same input gives same top 5."},
]

CATEGORY_COLORS = {
    "Luda Apr 15": "#3b82f6",      # blue
    "Luda Apr 28": "#8b5cf6",      # purple
    "Vivek Apr 29 (NEW today)": "#10b981",  # green
    "Vivek Apr 29 (NEW)": "#10b981",
    "Vivek depth fix": "#f59e0b",  # amber
    "Vivek spec": "#f59e0b",
    "Vivek + Apr 30": "#10b981",
    "User Apr 30 (NEW)": "#ef4444", # red
}


def render_html():
    # Read profile/path/lesson IDs from the markdown report if available
    md_path = REPORT_DIR / "WALKTHROUGH_REPORT.md"
    pid = path_id = lesson_id = ""
    if md_path.exists():
        text = md_path.read_text(encoding="utf-8")
        for line in text.split("\n"):
            if "Test profile created" in line:
                pid = line.split(":")[1].strip().split()[0]
            if "Test learning path:" in line:
                path_id = line.split("`")[1] if "`" in line else ""
            if "Test lesson:" in line:
                lesson_id = line.split("`")[1] if "`" in line else ""

    base = "http://95.216.199.47:3000"

    def url(template):
        return base + template.format(pid=pid, path_id=path_id, lesson_id=lesson_id)

    # Build the cards
    cards_html = []
    toc_items = []

    for i, c in enumerate(CHANGES, 1):
        color = CATEGORY_COLORS.get(c["category"], "#6b7280")
        full_url = url(c["page_url"])
        files_html = "".join(f"<li><code>{f}</code></li>" for f in c["files"])

        toc_items.append(
            f'<li><a href="#change-{c["id"]}"><span class="num">{i}</span>{c["title"]}</a>'
            f'<span class="cat-pill" style="background:{color}">{c["category"]}</span></li>'
        )

        screenshot_html = (
            f'<a href="{c["id"]}.png" target="_blank" class="shot">'
            f'<img src="{c["id"]}.png" alt="{c["title"]}" loading="lazy">'
            f'<div class="zoom-hint">Click to enlarge</div></a>'
        )

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
    </div>
</div>
''')

    # Build the HTML
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
.layout {{ display: grid; grid-template-columns: 320px 1fr; min-height: 100vh; }}
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
.toc {{ list-style: none; padding: 0; margin: 0; }}
.toc li {{
    margin: 0;
    padding: 6px 0;
    border-top: 1px solid #f3f4f6;
}}
.toc a {{
    text-decoration: none;
    color: #1f2937;
    font-size: 13px;
    display: block;
    padding: 4px 6px;
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
.main {{ padding: 32px 40px; max-width: 1100px; }}
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
.section:last-child {{ margin-bottom: 0; }}
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
.card.hidden {{ display: none; }}
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
        <div class="sub">{len(CHANGES)} changes deployed Apr 28 - May 5</div>
        <input type="search" placeholder="Search changes..." id="search">
        <ul class="toc">
            {"".join(toc_items)}
        </ul>
    </aside>
    <main class="main">
        <div class="page-head">
            <h1>AI Pathway - Visual Changes Walkthrough</h1>
            <div class="summary">
                Tool URL: <strong><a href="{base}/" target="_blank">{base}</a></strong><br>
                {len(CHANGES)} visual changes covering Luda Apr 15 + Apr 28 feedback, Vivek Apr 29 critique,
                and the new Implementation Task workflow. Click any screenshot to enlarge.
            </div>
            <div class="cat-filters">
                <button class="cat-btn active" data-cat="all">All ({len(CHANGES)})</button>
                {"".join(f'<button class="cat-btn" data-cat="{cat}" style="border-color:{color}">{cat}</button>' for cat, color in CATEGORY_COLORS.items() if any(c["category"] == cat for c in CHANGES))}
            </div>
        </div>
        {"".join(cards_html)}
    </main>
</div>
<script>
// Search filter
const search = document.getElementById('search');
search.addEventListener('input', () => {{
    const q = search.value.toLowerCase().trim();
    document.querySelectorAll('.card').forEach(card => {{
        const text = card.dataset.search || '';
        card.classList.toggle('hidden', q && !text.includes(q));
    }});
    // Update TOC visibility too
    document.querySelectorAll('.toc li').forEach(li => {{
        const link = li.querySelector('a');
        if (!link) return;
        const target = document.querySelector(link.getAttribute('href'));
        li.style.display = (target && !target.classList.contains('hidden')) ? '' : 'none';
    }});
}});

// Category filters
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

// Copy URL buttons
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
