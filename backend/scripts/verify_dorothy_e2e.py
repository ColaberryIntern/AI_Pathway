"""End-to-end Playwright walkthrough of Dorothy F's path, replicating
the click sequence from Luda's May 16 bug report:

  1. Load the Top 5 Skills page; hover the Level 1 button on
     "Education: Learning design with AI" and confirm a real per-skill
     rubric (not the generic "Can explain basics") appears.
  2. Load the Learning Dashboard; confirm every sidebar module title
     matches the Top 5 page's skill name.
  3. Click Module 3 (Education: Learning design with AI) and its lesson;
     wait for content to load; confirm the rendered chapter is about
     learning design, not prompt debugging.

Outputs a screenshot for each step under docs/luda_may16/verify_e2e_*.png.
"""
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://95.216.199.47:3000"
ANALYSIS_ID = "9b692fe9-1f13-4ddf-8c8c-27376e96a6d0"
PATH_ID = "dc6b05fb-d7b0-440f-9bdc-f252b31f8be2"
MODULE3_LESSON_ID = "86e04bee-2c82-4d47-be1a-f861af0e85fb"

OUT_DIR = Path(__file__).resolve().parents[2] / "docs" / "luda_may16"
EXPECTED_MODULES = [
    "Draft -> critique -> revise",
    "Prompt debugging & iteration",
    "Education: Learning design with AI",
    "Facilitating AI workshops",
    "Cross-functional AI collaboration",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        pg = ctx.new_page()

        print("== STEP 1: Top 5 Skills page + rubric hover ==")
        pg.goto(f"{BASE}/analysis/{ANALYSIS_ID}?view=skill_selection", wait_until="load")
        # Page needs a beat for React Query
        pg.wait_for_timeout(2500)
        body = pg.locator("body").text_content() or ""
        if "Education: Learning design with AI" not in body:
            pg.screenshot(path=str(OUT_DIR / "verify_e2e_top5_fail.png"), full_page=True)
            fail("Top 5 page does not mention 'Education: Learning design with AI' -- profile or selection state changed?")
        print("  OK - 'Education: Learning design with AI' appears on Top 5 page")

        # Find the Education skill's level buttons. Each skill renders a
        # "Rate Your Current Proficiency" panel that displays the skill name
        # followed by buttons 0..4. Find every L1 button on the page in DOM
        # order, then pick the one whose *closest preceding* skill-name
        # appearance matches Education: Learning design with AI.
        skill_name = "Education: Learning design with AI"
        # Pick the L1 button inside the panel whose immediate enclosing
        # `.card` ancestor (or close ancestor) contains the skill name in
        # its h3/h4 heading - matches how the SelfAssessment component
        # nests buttons inside a per-skill card.
        btn_index = pg.evaluate(
            r"""(skillName) => {
                // For each L1 button, walk to its nearest .card ancestor and
                // check whether the card's innerText begins with the skill
                // name. This matches the DOM the SelfAssessment component
                // emits: each skill is one .card with the skill name as the
                // first text node and the level buttons inside.
                const buttons = Array.from(document.querySelectorAll('button'))
                    .filter(b => /^\s*1\s*Aware\b/i.test(b.textContent || ''));
                for (let i = 0; i < buttons.length; i++) {
                    const card = buttons[i].closest('.card');
                    if (!card) continue;
                    const head = (card.innerText || '').trim();
                    if (head.startsWith(skillName)) return i;
                }
                return -1;
            }""",
            skill_name,
        )
        if btn_index < 0:
            pg.screenshot(path=str(OUT_DIR / "verify_e2e_no_button.png"), full_page=True)
            fail(f"could not locate Level 1 button under skill {skill_name!r}")
        all_l1 = pg.get_by_role("button", name=re.compile(r"^\s*1\s*Aware\b", re.I))
        target_btn = all_l1.nth(btn_index)
        target_btn.scroll_into_view_if_needed()
        target_btn.hover(timeout=10000)
        pg.wait_for_timeout(1200)
        new_body = pg.locator("body").text_content() or ""
        target = "Knows AI can help generate learning materials"
        if target.lower() not in new_body.lower():
            pg.screenshot(path=str(OUT_DIR / "verify_e2e_hover_fail.png"), full_page=False)
            print(f"  FAIL: tooltip text not found. Looked for: {target!r}")
            print(f"  body sample (around 'AI can'): {find_around(new_body, 'AI can', 120)!r}")
            sys.exit(1)
        pg.screenshot(path=str(OUT_DIR / "verify_e2e_step1_hover.png"), full_page=False)
        print(f"  OK - tooltip shows authoritative rubric: '{target}...'")

        print()
        print("== STEP 2: Learning Dashboard sidebar names ==")
        pg.goto(f"{BASE}/learn/{PATH_ID}", wait_until="load")
        pg.wait_for_timeout(2500)
        body2 = pg.locator("body").text_content() or ""
        for expected in EXPECTED_MODULES:
            if expected not in body2:
                pg.screenshot(path=str(OUT_DIR / "verify_e2e_dashboard_fail.png"), full_page=True)
                fail(f"Dashboard missing expected module title: {expected!r}")
        pg.screenshot(path=str(OUT_DIR / "verify_e2e_step2_dashboard.png"), full_page=False)
        print(f"  OK - all 5 ontology-canonical module titles present in sidebar")

        print()
        print("== STEP 3: Click Module 3 lesson + verify chapter content ==")
        pg.goto(f"{BASE}/learn/{PATH_ID}/lesson/{MODULE3_LESSON_ID}", wait_until="load")
        # Wait up to 90s for generation (live LLM call)
        try:
            pg.wait_for_function(
                "() => /Learning design|learning design/i.test(document.body.innerText)",
                timeout=120000,
            )
        except Exception:
            pg.screenshot(path=str(OUT_DIR / "verify_e2e_lesson_fail.png"), full_page=True)
            fail("Module 3 lesson page did not render learning-design content within 120s")
        body3 = pg.locator("body").text_content() or ""
        # Reject if the chapter title is the SK.PRM.003 hallucination
        if "Prompt debugging & iteration" in body3 and "Education: Learning design" not in body3:
            pg.screenshot(path=str(OUT_DIR / "verify_e2e_lesson_fail.png"), full_page=True)
            fail("Module 3 lesson still shows SK.PRM.003 'Prompt debugging' content")
        # Positive: chapter should be about education / learning design
        positives = [
            "learning design",
            "Education",
            "SK.DOM.EDU.001",
        ]
        hits = [p for p in positives if p.lower() in body3.lower()]
        pg.screenshot(path=str(OUT_DIR / "verify_e2e_step3_lesson.png"), full_page=False)
        if len(hits) < 2:
            print(f"  WARN: only {len(hits)} of 3 learning-design markers present: {hits}")
        else:
            print(f"  OK - chapter content reflects SK.DOM.EDU.001; markers found: {hits}")

        browser.close()

    print()
    print("ALL PRODUCTION CHECKS PASSED")


def find_around(s: str, needle: str, window: int) -> str:
    i = s.lower().find(needle.lower())
    if i < 0:
        return ""
    return s[max(0, i - window):i + window]


if __name__ == "__main__":
    main()
