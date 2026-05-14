"""Generate a comprehensive walkthrough report for all visual changes.

For each change:
- Live URL where to find it
- Screenshot with the changed element highlighted with a red rectangle
- Step-by-step explanation of what was changed and why

Uses Playwright + JS injection to draw the red highlights at runtime
so the highlights are part of the rendered page (no PIL post-processing).
"""
import asyncio
import json
import sys
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

BASE = "http://95.216.199.47:3000"
API = f"{BASE}/api"
REPORT_DIR = Path(__file__).parent.parent.parent / "docs" / "walkthrough_report"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR = REPORT_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

JENNIFER_JD = (
    "AI Content Editor. Evaluate and edit AI-generated content for accuracy, "
    "tone, and clarity. Collaborate with developers to refine content generation "
    "algorithms. Develop AI content disclosure guidelines. Review AI outputs for "
    "bias and factual accuracy. Implement quality evaluation frameworks. "
    "IP and copyright considerations."
)

JENNIFER_PROFILE = {
    "name": "Walkthrough Report Test",
    "current_role": "Content Editor",
    "industry": "Corporate Communications",
    "experience_years": 9,
    "ai_exposure_level": "Basic",
    "technical_background": "No coding experience",
    "learning_intent": "Content creation",
    "target_jd_text": JENNIFER_JD,
    "tools_used": ["ChatGPT / Claude / Gemini"],
}

# JavaScript helper that draws a red rectangle around a CSS selector
HIGHLIGHT_JS = """
(args) => {
    const { selector, label, contains } = args;
    let elements = [];
    if (contains) {
        // Find elements containing specific text
        const all = document.querySelectorAll(selector || '*');
        elements = Array.from(all).filter(el => el.textContent && el.textContent.includes(contains));
    } else if (selector) {
        elements = Array.from(document.querySelectorAll(selector));
    }
    // Use the smallest matching element (most specific)
    elements.sort((a, b) => (a.getBoundingClientRect().width * a.getBoundingClientRect().height) - (b.getBoundingClientRect().width * b.getBoundingClientRect().height));
    const target = elements[0];
    if (!target) return false;
    const rect = target.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return false;
    target.scrollIntoView({behavior: 'instant', block: 'center'});
    // Add overlay div
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    const r = target.getBoundingClientRect();
    overlay.style.top = (r.top - 8) + 'px';
    overlay.style.left = (r.left - 8) + 'px';
    overlay.style.width = (r.width + 16) + 'px';
    overlay.style.height = (r.height + 16) + 'px';
    overlay.style.border = '4px solid #ef4444';
    overlay.style.borderRadius = '8px';
    overlay.style.zIndex = '99999';
    overlay.style.pointerEvents = 'none';
    overlay.style.boxShadow = '0 0 0 2px rgba(255,255,255,0.8)';
    overlay.id = 'walkthrough-highlight';
    document.body.appendChild(overlay);
    if (label) {
        const lbl = document.createElement('div');
        lbl.style.position = 'fixed';
        lbl.style.top = (r.top - 32) + 'px';
        lbl.style.left = (r.left - 8) + 'px';
        lbl.style.background = '#ef4444';
        lbl.style.color = 'white';
        lbl.style.padding = '2px 8px';
        lbl.style.fontSize = '12px';
        lbl.style.fontWeight = 'bold';
        lbl.style.borderRadius = '4px';
        lbl.style.zIndex = '99999';
        lbl.id = 'walkthrough-label';
        lbl.textContent = label;
        document.body.appendChild(lbl);
    }
    return true;
}
"""

CLEAR_HIGHLIGHT_JS = """
() => {
    const ovl = document.getElementById('walkthrough-highlight');
    if (ovl) ovl.remove();
    const lbl = document.getElementById('walkthrough-label');
    if (lbl) lbl.remove();
}
"""


async def create_profile() -> str | None:
    """Create the test profile only. Returns the profile id, or None on failure."""
    print("Creating test profile...")
    async with httpx.AsyncClient(timeout=240) as client:
        r = await client.post(f"{API}/profiles/", json=JENNIFER_PROFILE)
        if r.status_code not in (200, 201):
            print(f"  FAIL: {r.status_code}")
            return None
        pid = r.json()["id"]
        print(f"  Profile: {pid}")
        return pid


async def complete_analysis_and_chapter(pid: str) -> tuple[str | None, str | None]:
    """Run analysis, activate path, generate first chapter. Returns (path_id, lesson_id)."""
    print("Running analysis + chapter generation...")
    async with httpx.AsyncClient(timeout=240) as client:
        r = await client.post(f"{API}/analysis/full", json={
            "profile_id": pid,
            "target_jd_text": JENNIFER_JD,
            "target_role": "AI Content Editor",
            "skip_assessment": True,
        })
        if r.status_code != 200:
            print(f"  FAIL analysis: {r.status_code}")
            return None, None
        path_id = r.json().get("learning_path_id")
        print(f"  Path: {path_id}")

        r = await client.post(f"{API}/learning/{path_id}/activate")
        modules = r.json().get("modules", [])
        first_lesson_id = modules[0].get("lesson_outline", [{}])[0].get("id") if modules else None
        print(f"  Lesson: {first_lesson_id}")

        if first_lesson_id:
            print("  Generating chapter (~30-60s)...")
            r = await client.post(f"{API}/learning/{path_id}/lessons/{first_lesson_id}/start", timeout=180)
            if r.status_code == 200:
                print("  Chapter generated.")

        return path_id, first_lesson_id


async def main():
    pid = await create_profile()
    if not pid:
        sys.exit(1)

    # Path and lesson IDs only exist after analysis runs. CHANGES still
    # references them in URL templates, so use empty strings as placeholders
    # for pre-analysis items (they don't navigate to /learn anyway).
    path_id = ""
    lesson_id = ""

    # Each entry: dict with keys: id, title, page_url, click_path, highlight_selector, highlight_text, description, what_changed, why_changed
    changes = [
        {
            "id": "01_homepage_simplified",
            "title": "Homepage simplified",
            "page_url": f"{BASE}/",
            "highlight_selector": "h1",  # the hero
            "highlight_label": "Hero (sole content)",
            "what_changed": "Removed 'How It Works' section and 'Ready to start your AI learning journey?' CTA block.",
            "why_changed": "Per Luda Apr 15: page should fit on a single screen. Was previously requiring multiple scrolls.",
            "files_modified": ["frontend/src/pages/HomePage.tsx"],
        },
        {
            "id": "02_profiles_copy",
            "title": "Profiles page copy update",
            "page_url": f"{BASE}/profiles",
            "highlight_text": "different career goals",
            "highlight_label": "New copy",
            "what_changed": "Subhead changed from 'Create and manage learner profiles' to 'Create profiles for different career goals'.",
            "why_changed": "Per Luda Apr 15: language tailored for individuals creating multiple profiles for themselves.",
            "files_modified": ["frontend/src/pages/ProfileSelectionPage.tsx"],
        },
        {
            "id": "03_skills_review_merged",
            "title": "Skill selection + self-assessment merged",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_text": "Top 5 Skills for the Targeted Role",
            "highlight_label": "Merged page heading",
            "what_changed": "Combined two previously separate pages (skill selection, then self-assessment) into one unified page. When a skill is selected, the proficiency rating appears inline below it.",
            "why_changed": "Per Luda Apr 15: reduce step count and let user adjust skills + ratings in one view.",
            "files_modified": ["frontend/src/pages/AnalysisPage.tsx", "frontend/src/components/SelfAssessment.tsx"],
            "phase": "pre_analysis",
        },
        {
            "id": "04_skill_hover_tooltip",
            "title": "Hover tooltip with ontology description on skill name",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_selector": "h3",
            "highlight_text": "Prompt debugging",
            "highlight_label": "Hover for ontology description",
            "what_changed": "Skill names now have a dotted underline + cursor:help. Hovering shows the canonical ontology description and skill_id in a dark tooltip.",
            "why_changed": "Per Vivek Apr 29 (confirmed Agreed): users shouldn't have to guess what a skill means. Show the authoritative ontology definition on hover.",
            "files_modified": ["frontend/src/components/SelfAssessment.tsx", "frontend/src/pages/AnalysisPage.tsx"],
            "hover_first": True,
            "phase": "pre_analysis",
        },
        {
            "id": "05_targeted_role_label",
            "title": "Detected Role -> Targeted Role rename",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_text": "Targeted role",  # New label after rename
            "highlight_label": "Renamed from 'Detected role'",
            "what_changed": "Label 'Detected role' renamed to 'Targeted role' throughout the tool.",
            "why_changed": "Per Luda Apr 15: 'Targeted' is more accurate - the user is selecting a target, not having a role 'detected'.",
            "files_modified": ["frontend/src/components/profile/TargetGoalPanel.tsx"],
            "phase": "pre_analysis",
        },
        {
            "id": "06_skill_match_messaging",
            "title": "End-of-page messaging when skills match target",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_text": "build a learning path consisting of 5 chapters",
            "highlight_label": "New messaging (only shows if skills are at target)",
            "what_changed": "Changed messaging from 'we will proceed with the remaining X skills' to 'we will add other relevant skills to build a learning path consisting of 5 chapters'.",
            "why_changed": "Per Luda Apr 28: clarify that the system backfills with new skills rather than just dropping the matched ones.",
            "files_modified": ["frontend/src/pages/AnalysisPage.tsx"],
            "may_not_render": True,  # only shows when skills are at target
            "phase": "pre_analysis",
        },
        {
            "id": "07_learning_dashboard_no_gate",
            "title": "Learning dashboard auto-activates (no Ready to Start gate)",
            "page_url": f"{BASE}/learn/{path_id}",
            "highlight_selector": "h1, h2",
            "highlight_label": "Dashboard renders directly (no gate)",
            "what_changed": "Removed 'Ready to Start Learning?' confirmation page that previously appeared between skill review and the dashboard. Path now auto-activates on load.",
            "why_changed": "Per Luda Apr 28: the gate page was duplicative of the skill review confirmation. Goes straight to the chapters.",
            "files_modified": ["frontend/src/pages/LearningDashboardPage.tsx"],
        },
        {
            "id": "08_journey_roadmap_removed",
            "title": "Your Journey Roadmap page removed",
            "page_url": f"{BASE}/analysis/{pid}",
            "highlight_text": "Continue to Learning Path",
            "highlight_label": "Now goes directly to dashboard",
            "what_changed": "Removed the entire 'Your Journey Roadmap' page that previously appeared between skill review and the learning dashboard. Continue to Learning Path button now goes straight to the chapters.",
            "why_changed": "Per Luda Apr 28: the roadmap page was duplicative - same info already shown on the skill review page.",
            "files_modified": ["frontend/src/pages/AnalysisPage.tsx"],
        },
        {
            "id": "09_chapter_section_nav",
            "title": "Chapter section navigation (6 sections, 15 min)",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "highlight_text": "Assignment",
            "highlight_label": "All 6 section tabs incl. NEW Assignment",
            "what_changed": "Chapter renderer shows 6 section tabs at top: Scenario (2m), Concepts (3m), Example 1 (3m), Example 2 (4m), Build (3m), Assignment (30m). The Assignment tab is the new 6th section.",
            "why_changed": "Per Vivek's chapter spec (5 sections totaling 15 min) + user's request to bring back the Implementation Task assignment workflow as a 6th section.",
            "files_modified": ["frontend/src/components/chapter/ChapterRenderer.tsx", "backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md"],
        },
        {
            "id": "10_chapter_title_ontology_name",
            "title": "Chapter title uses ontology canonical name",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "highlight_selector": "h1",
            "highlight_label": "Ontology name (was story-style title)",
            "what_changed": "Chapter title now displays the ontology canonical skill name (e.g. 'Prompt debugging & iteration') instead of the LLM-generated story title (e.g. 'Iterating on Prompts: From Literacy to Practitioner'). The story title moved to subtitle position.",
            "why_changed": "Per Vivek Apr 29 (confirmed Agreed) on Luda's request: skills should be named consistently using ontology names throughout the tool.",
            "files_modified": ["frontend/src/components/chapter/ChapterRenderer.tsx"],
        },
        {
            "id": "11_concepts_with_mnemonic",
            "title": "Concepts section with mnemonic + pull_quote",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "click_tab": "Concepts",
            "highlight_text": "IVL",  # may not match if mnemonic differs - fall through gracefully
            "highlight_label": "Mnemonic (e.g. 'IVL = Isolate, Vary, Log')",
            "what_changed": "Concepts section now requires a mnemonic field (e.g. 'IVL'), a pull_quote (single memorable sentence), and 2-4 concept cards each with identifier, word, headline, body, analogy, color_role.",
            "why_changed": "Per Vivek's depth spec: chapters lacked structural depth. Mnemonic + pull_quote are anchor elements that help retention.",
            "files_modified": ["backend/app/data/chapter-generator-prompt.md", "backend/app/agents/chapter_generator.py"],
        },
        {
            "id": "12_example1_steps_array",
            "title": "Example 1 with 3-step structure (diagnosis_checklist / prompt_variant / log_entry)",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "click_tab": "Example 1",
            "highlight_text": "Step 1",
            "highlight_label": "3-step structured walkthrough",
            "what_changed": "Example 1 now requires a steps array with EXACTLY 3 entries: (1) diagnosis_checklist with broken/clear status flags, (2) prompt_variant ref, (3) log_entry table with key/value pairs (prompt_id, change, output_quality, lesson, reuse).",
            "why_changed": "Per Vivek's spec: Example 1 should walk learner through the diagnostic process, not just show a prompt and result. The structured steps reinforce the methodology.",
            "files_modified": ["backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md", "frontend/src/components/chapter/ChapterRenderer.tsx"],
        },
        {
            "id": "13_example2_ab_comparison",
            "title": "Example 2 A/B comparison",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "click_tab": "Example 2",
            "highlight_selector": ".grid-cols-2",
            "highlight_label": "A/B side-by-side comparison",
            "what_changed": "Example 2 must have a comparison object with test_question, exactly 2 variants (id A, id B) with full prompt/output/rating/why, and a takeaway.",
            "why_changed": "Per Vivek's spec: Example 2 demonstrates the target-level skill (A/B testing) by example, not just description.",
            "files_modified": ["backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md"],
        },
        {
            "id": "14_agent_build_section",
            "title": "Build Your Agent section",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "click_tab": "Build",
            "highlight_text": "Personalize your agent",
            "highlight_label": "3 personalization fields + system prompt template",
            "what_changed": "Agent Build section requires: 3 capability_chips, 3 personalization_fields (text/textarea inputs), a system_prompt_template that interpolates the {key} placeholders, usage_steps, and final_affirmation tying back to the rubric.",
            "why_changed": "Per Vivek's spec: each chapter ends with a takeaway artifact the learner can use the same day.",
            "files_modified": ["backend/app/agents/chapter_generator.py", "frontend/src/components/chapter/ChapterRenderer.tsx"],
        },
        {
            "id": "15_try_in_llm_buttons",
            "title": "Try-in-LLM buttons (Run in ChatGPT)",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "click_tab": "Example 1",
            "highlight_text": "Run in ChatGPT",
            "highlight_label": "NEW: Send prompt to LLM",
            "what_changed": "Added 'Run in ChatGPT' / 'Run in Claude' buttons next to every prompt in the chapter: original_prompt, iterated_prompt, A/B variants, and the interpolated agent build template. Listens to llm-changed event so labels update when user switches LLM.",
            "why_changed": "Per Vivek Apr 29: 'I also liked aspects of your previous build especially around giving links to try out the prompts in chatgpt or claude.' Brought back from the older build.",
            "files_modified": ["frontend/src/components/chapter/ChapterRenderer.tsx"],
        },
        {
            "id": "16_implementation_task_section",
            "title": "Implementation Task as 6th section (NEW)",
            "page_url": f"{BASE}/learn/{path_id}/lesson/{lesson_id}",
            "click_tab": "Assignment",
            "highlight_text": "Your turn",
            "highlight_label": "NEW 6th section: hands-on assignment + AI grading",
            "what_changed": "Brought back the Implementation Task assignment workflow as a 6th chapter section. Includes title, description, 3-5 requirements, deliverable, tools (free/paid badges), evidence_requirements (file uploads), 30-60 min estimate. Submit & Get Graded uses the existing AI grading endpoint. Mentor briefing step hidden via hideMentorStep prop.",
            "why_changed": "Per user's Apr 30 request: the assignment functionality from the old multi-lesson format was missing. Vivek's chapter format only had the Build section (which produces an agent template), not a graded assignment that produces an artifact.",
            "files_modified": ["backend/app/agents/chapter_generator.py", "backend/app/data/chapter-generator-prompt.md", "frontend/src/components/chapter/ChapterRenderer.tsx", "frontend/src/components/learning/ImplementationTaskCard.tsx"],
        },
        {
            "id": "17_deterministic_skill_ordering",
            "title": "Deterministic skill ordering between runs",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_text": "Top 5",
            "highlight_label": "Same input -> same top 5 every run",
            "what_changed": "Set profile_analyzer LLM call to temperature=0 (was 0.3). Combined with already-zero temperature on JD parser and gap analyzer. Verified across 20 consecutive runs - identical top 5 every time.",
            "why_changed": "Per Luda Apr 28: she ran Jennifer C twice and got different top 5 skills. The variance came from the profile analyzer's LLM call running at a non-zero temperature.",
            "files_modified": ["backend/app/agents/profile_analyzer.py"],
            "phase": "pre_analysis",
        },
        {
            "id": "18_skill_rank_sequential",
            "title": "Skills now render in sequential rank order (no duplicate or skipped numbers)",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_selector": "h1",
            "highlight_label": "Ranks #1..#N sequential, in render order",
            "what_changed": "Backend now normalizes skill ranks to sequential 1..N at the end of JD parsing AND after the rerank/enrich step. Frontend defensively renumbers on revisit. Previously a single render could show duplicate #2 and skip #7, with the rank-1 skill appearing 5th instead of 1st.",
            "why_changed": "Per Luda May 9 ad-hoc feedback: she opened the JC profile and saw 'the #1 skill (draft -> critique -> revise) appears at the end of the top 5' plus two #2s and no #7.",
            "files_modified": ["backend/app/agents/jd_parser.py", "backend/app/api/routes/analysis.py", "frontend/src/pages/AnalysisPage.tsx"],
            "phase": "pre_analysis",
        },
        {
            "id": "19_dashboard_back_to_skill_review",
            "title": "Back to skill review link on the Learning Dashboard",
            "page_url": f"{BASE}/learn/{path_id}",
            "highlight_text": "Back to skill review",
            "highlight_label": "New back-link in dashboard header",
            "what_changed": "Learning Dashboard header now includes a Back to skill review link that routes to /analysis/{profile_id}?view=skill_selection. Backend dashboard endpoint exposes profile_id (looked up via the path's goal). Frontend renders the link when present.",
            "why_changed": "Per Luda May 9 ad-hoc feedback: 'After I progress from that page to the AI Learning Path Dashboard, I cannot come back to the full list.'",
            "files_modified": ["backend/app/schemas/learning.py", "backend/app/api/routes/learning.py", "frontend/src/types/index.ts", "frontend/src/pages/LearningDashboardPage.tsx"],
        },
        {
            "id": "20_rating_persistence",
            "title": "Proficiency ratings persist across navigation",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_text": "assessed",
            "highlight_label": "Ratings survive nav away and back via localStorage",
            "what_changed": "selfAssessedSkills state now reads from and writes to localStorage keyed by profileId. Previously the state was useState-only, so navigating to /learn and returning reset all ratings to empty (counter back to 0/5 assessed).",
            "why_changed": "Per Luda May 9 ad-hoc PDF: rated 5 skills but the next visit showed 0/5 assessed. State was being thrown away on every page mount.",
            "files_modified": ["frontend/src/pages/AnalysisPage.tsx"],
            "phase": "pre_analysis",
        },
        {
            "id": "21_per_skill_hover_descriptions",
            "title": "Hover tooltip shows per-skill, per-level rubric (not generic)",
            "page_url": f"{BASE}/analysis/{pid}?view=skill_selection",
            "highlight_selector": "button",
            "highlight_text": "Practitioner",
            "highlight_label": "Per-skill description per level",
            "what_changed": "Ontology service now reads rubric_by_level (which is populated for every skill) and converts it to the proficiency_descriptions structure the frontend expects. Previously the service looked for a different field name and fell back to a generic 5-line scale (e.g. 'Practitioner: Can adapt independently' for every skill). Now each skill shows its own rubric: e.g. SK.PRM.003 L1 = 'Knows that prompts can be revised when output is unsatisfactory'.",
            "why_changed": "Per Vivek May 9 walkthrough feedback (item 04): wanted per-skill, per-level descriptions matching his ai-fluency-assessment ontology. Per Luda Apr 29: 'Pull from the ontology the description of the proficiency level for EACH skill.'",
            "files_modified": ["backend/app/services/ontology.py"],
            "phase": "pre_analysis",
        },
    ]

    async def capture_one(change: dict, page) -> None:
        """Navigate, optionally hover/click, highlight, screenshot. Mutates change dict."""
        try:
            # `domcontentloaded` fires as soon as the DOM is parsed; we then
            # wait for the highlight target text to appear (or a default
            # timeout) instead of relying on networkidle, which can never
            # fire on the analysis page because the skill-parsing LLM call
            # holds the network busy beyond Playwright's 30s ceiling.
            await page.goto(change["page_url"], wait_until="domcontentloaded", timeout=60000)
            target_text = change.get("highlight_text")
            if target_text:
                try:
                    await page.wait_for_function(
                        "(t) => document.body && document.body.textContent && document.body.textContent.includes(t)",
                        arg=target_text,
                        timeout=45000,
                    )
                except Exception:
                    pass
            await page.wait_for_timeout(1500)

            if change.get("click_tab"):
                try:
                    tab = await page.query_selector(f'button:has-text("{change["click_tab"]}")')
                    if tab:
                        await tab.click()
                        await page.wait_for_timeout(1500)
                except Exception:
                    pass

            if change.get("hover_first"):
                try:
                    target = await page.query_selector("h3.cursor-help")
                    if target:
                        await target.hover()
                        await page.wait_for_timeout(800)
                except Exception:
                    pass

            args = {
                "selector": change.get("highlight_selector"),
                "contains": change.get("highlight_text"),
                "label": change.get("highlight_label", ""),
            }
            args = {k: v for k, v in args.items() if v is not None}
            highlighted = await page.evaluate(HIGHLIGHT_JS, args)
            if not highlighted:
                # Content may still be loading. Wait and retry once.
                await page.wait_for_timeout(3000)
                highlighted = await page.evaluate(HIGHLIGHT_JS, args)
            if not highlighted:
                print(f"    (could not highlight, taking page screenshot)")
            await page.wait_for_timeout(500)

            shot_path = SCREENSHOTS_DIR / f"{change['id']}.png"
            await page.screenshot(path=str(shot_path), full_page=False)
            change["screenshot"] = f"screenshots/{shot_path.name}"

            await page.evaluate(CLEAR_HIGHLIGHT_JS)
        except Exception as e:
            print(f"    failed: {e}")
            change["screenshot"] = None
            change["error"] = str(e)[:100]

    # Phase 1: capture pre-analysis screenshots (skill_selection step).
    # The page lands on jd_input briefly, auto-load fails (no analysis yet),
    # falls into parseJDSkills, sets step='skill_selection'. That is the
    # state these items document.
    pre_changes = [c for c in changes if c.get("phase") == "pre_analysis"]
    print(f"\n[Phase 1] Capturing {len(pre_changes)} pre-analysis screenshots...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1100})
        for c in pre_changes:
            print(f"  - {c['id']}: {c['title']}")
            await capture_one(c, page)
        await browser.close()

    # Run analysis + activate path + generate first chapter so post-analysis
    # URLs (/learn/...) actually have content.
    path_id, lesson_id = await complete_analysis_and_chapter(pid)
    if not path_id:
        sys.exit(1)

    # Fill in the post-analysis URL placeholders. CHANGES was built with
    # path_id="" / lesson_id="" so /learn URLs were malformed.
    PATH_AND_LESSON_IDS = {
        "09_chapter_section_nav", "10_chapter_title_ontology_name",
        "11_concepts_with_mnemonic", "12_example1_steps_array",
        "13_example2_ab_comparison", "14_agent_build_section",
        "15_try_in_llm_buttons", "16_implementation_task_section",
    }
    for c in changes:
        if c["id"] == "07_learning_dashboard_no_gate":
            c["page_url"] = f"{BASE}/learn/{path_id}"
        elif c["id"] in PATH_AND_LESSON_IDS:
            c["page_url"] = f"{BASE}/learn/{path_id}/lesson/{lesson_id}"

    # Phase 2: capture post-analysis screenshots.
    post_changes = [c for c in changes if c.get("phase") != "pre_analysis"]
    print(f"\n[Phase 2] Capturing {len(post_changes)} post-analysis screenshots...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1100})
        for c in post_changes:
            print(f"  - {c['id']}: {c['title']}")
            await capture_one(c, page)
        await browser.close()

    # NOTE: Test profile is intentionally kept alive after the run so the
    # live URLs in the walkthrough HTML actually work for the reviewer.
    # Run scripts/walkthrough_cleanup.py to delete it once the review round
    # is complete.
    print("\nKeeping profile alive for client review (run walkthrough_cleanup.py to remove later).")

    # ===== Generate report =====
    print("\nWriting report...")
    lines = ["# AI Pathway - Visual Changes Walkthrough Report", ""]
    lines.append(f"Generated: {asyncio.get_event_loop().time()}")
    lines.append("")
    lines.append("**Tool URL:** http://95.216.199.47:3000")
    lines.append("")
    lines.append(f"**Test profile created for this report:** `{pid}` (kept alive for review)")
    lines.append(f"**Test learning path:** `{path_id}`")
    lines.append(f"**Test lesson:** `{lesson_id}`")
    lines.append("")
    lines.append("Each section below covers one visual change. The screenshot shows the change with a red rectangle around the affected element.")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, change in enumerate(changes, 1):
        lines.append(f"## {i}. {change['title']}")
        lines.append("")
        lines.append(f"**Live URL:** {change['page_url']}")
        lines.append("")
        if change.get("click_tab"):
            lines.append(f"**To see this change:** Open the URL above, then click the **{change['click_tab']}** tab.")
            lines.append("")
        elif change.get("hover_first"):
            lines.append(f"**To see this change:** Open the URL above, then hover over a skill name.")
            lines.append("")
        else:
            lines.append("**To see this change:** Open the URL above.")
            lines.append("")

        if change.get("screenshot"):
            lines.append(f"![{change['title']}]({change['screenshot']})")
            lines.append("")
        elif change.get("error"):
            lines.append(f"_(Screenshot failed: {change['error']})_")
            lines.append("")

        lines.append("**What was changed:**")
        lines.append("")
        lines.append(change["what_changed"])
        lines.append("")
        lines.append("**Why:**")
        lines.append("")
        lines.append(change["why_changed"])
        lines.append("")
        lines.append("**Files modified:**")
        lines.append("")
        for f in change["files_modified"]:
            lines.append(f"- `{f}`")
        lines.append("")
        lines.append("---")
        lines.append("")

    out_path = REPORT_DIR / "WALKTHROUGH_REPORT.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nDone. Report: {out_path}")
    print(f"Screenshots: {REPORT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
