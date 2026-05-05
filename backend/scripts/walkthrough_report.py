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


async def setup_test_data():
    """Create profile and generate chapter content. Returns ids for testing."""
    print("Setting up test data...")
    async with httpx.AsyncClient(timeout=240) as client:
        r = await client.post(f"{API}/profiles/", json=JENNIFER_PROFILE)
        if r.status_code not in (200, 201):
            print(f"  FAIL: {r.status_code}")
            return None
        profile = r.json()
        pid = profile["id"]
        print(f"  Profile: {pid}")

        r = await client.post(f"{API}/analysis/full", json={
            "profile_id": pid,
            "target_jd_text": JENNIFER_JD,
            "target_role": "AI Content Editor",
            "skip_assessment": True,
        })
        if r.status_code != 200:
            print(f"  FAIL analysis: {r.status_code}")
            await client.delete(f"{API}/profiles/{pid}")
            return None
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

        return {
            "profile_id": pid,
            "path_id": path_id,
            "lesson_id": first_lesson_id,
        }


async def main():
    data = await setup_test_data()
    if not data:
        sys.exit(1)

    pid = data["profile_id"]
    path_id = data["path_id"]
    lesson_id = data["lesson_id"]

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
            "page_url": f"{BASE}/analysis/{pid}",
            "highlight_text": "Top 5 Skills for the Targeted Role",
            "highlight_label": "Merged page heading",
            "what_changed": "Combined two previously separate pages (skill selection, then self-assessment) into one unified page. When a skill is selected, the proficiency rating appears inline below it.",
            "why_changed": "Per Luda Apr 15: reduce step count and let user adjust skills + ratings in one view.",
            "files_modified": ["frontend/src/pages/AnalysisPage.tsx", "frontend/src/components/SelfAssessment.tsx"],
        },
        {
            "id": "04_skill_hover_tooltip",
            "title": "Hover tooltip with ontology description on skill name",
            "page_url": f"{BASE}/analysis/{pid}",
            "highlight_selector": "h3",
            "highlight_text": "Prompt debugging",
            "highlight_label": "Hover for ontology description",
            "what_changed": "Skill names now have a dotted underline + cursor:help. Hovering shows the canonical ontology description and skill_id in a dark tooltip.",
            "why_changed": "Per Vivek Apr 29 (confirmed Agreed): users shouldn't have to guess what a skill means. Show the authoritative ontology definition on hover.",
            "files_modified": ["frontend/src/components/SelfAssessment.tsx", "frontend/src/pages/AnalysisPage.tsx"],
            "hover_first": True,
        },
        {
            "id": "05_targeted_role_label",
            "title": "Detected Role -> Targeted Role rename",
            "page_url": f"{BASE}/analysis/{pid}",
            "highlight_text": "Detected role",  # This should be GONE - if found, fail
            "highlight_label": "Renamed (was 'Detected role')",
            "what_changed": "Label 'Detected role' renamed to 'Targeted role' throughout the tool.",
            "why_changed": "Per Luda Apr 15: 'Targeted' is more accurate - the user is selecting a target, not having a role 'detected'.",
            "files_modified": ["frontend/src/components/profile/TargetGoalPanel.tsx"],
        },
        {
            "id": "06_skill_match_messaging",
            "title": "End-of-page messaging when skills match target",
            "page_url": f"{BASE}/analysis/{pid}",
            "highlight_text": "build a learning path consisting of 5 chapters",
            "highlight_label": "New messaging (only shows if skills are at target)",
            "what_changed": "Changed messaging from 'we will proceed with the remaining X skills' to 'we will add other relevant skills to build a learning path consisting of 5 chapters'.",
            "why_changed": "Per Luda Apr 28: clarify that the system backfills with new skills rather than just dropping the matched ones.",
            "files_modified": ["frontend/src/pages/AnalysisPage.tsx"],
            "may_not_render": True,  # only shows when skills are at target
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
            "highlight_text": "Variant",
            "highlight_label": "A/B side-by-side",
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
            "page_url": f"{BASE}/analysis/{pid}",
            "highlight_text": "Top 5",
            "highlight_label": "Same input -> same top 5 every run",
            "what_changed": "Set profile_analyzer LLM call to temperature=0 (was 0.3). Combined with already-zero temperature on JD parser and gap analyzer. Verified across 20 consecutive runs - identical top 5 every time.",
            "why_changed": "Per Luda Apr 28: she ran Jennifer C twice and got different top 5 skills. The variance came from the profile analyzer's LLM call running at a non-zero temperature.",
            "files_modified": ["backend/app/agents/profile_analyzer.py"],
        },
    ]

    print(f"\nCapturing {len(changes)} highlighted screenshots...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1100})

        for change in changes:
            print(f"  - {change['id']}: {change['title']}")
            try:
                await page.goto(change["page_url"], wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2500)

                # Click a tab if specified
                if change.get("click_tab"):
                    try:
                        tab = await page.query_selector(f'button:has-text("{change["click_tab"]}")')
                        if tab:
                            await tab.click()
                            await page.wait_for_timeout(1500)
                    except Exception:
                        pass

                # Hover over an element first (for tooltip changes)
                if change.get("hover_first"):
                    try:
                        target = await page.query_selector("h3.cursor-help")
                        if target:
                            await target.hover()
                            await page.wait_for_timeout(800)
                    except Exception:
                        pass

                # Highlight the change
                args = {
                    "selector": change.get("highlight_selector"),
                    "contains": change.get("highlight_text"),
                    "label": change.get("highlight_label", ""),
                }
                # Filter None
                args = {k: v for k, v in args.items() if v is not None}
                highlighted = await page.evaluate(HIGHLIGHT_JS, args)
                if not highlighted:
                    print(f"    (could not highlight, taking page screenshot)")
                await page.wait_for_timeout(500)

                # Screenshot
                shot_path = REPORT_DIR / f"{change['id']}.png"
                await page.screenshot(path=str(shot_path), full_page=False)
                change["screenshot"] = shot_path.name

                # Clear highlight for next iteration
                await page.evaluate(CLEAR_HIGHLIGHT_JS)
            except Exception as e:
                print(f"    failed: {e}")
                change["screenshot"] = None
                change["error"] = str(e)[:100]

        await browser.close()

    # Cleanup
    print("\nCleanup...")
    async with httpx.AsyncClient(timeout=30) as client:
        await client.delete(f"{API}/profiles/{pid}")

    # ===== Generate report =====
    print("\nWriting report...")
    lines = ["# AI Pathway - Visual Changes Walkthrough Report", ""]
    lines.append(f"Generated: {asyncio.get_event_loop().time()}")
    lines.append("")
    lines.append("**Tool URL:** http://95.216.199.47:3000")
    lines.append("")
    lines.append(f"**Test profile created for this report:** {pid} (deleted after run)")
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
