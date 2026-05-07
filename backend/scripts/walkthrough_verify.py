"""Verify the walkthrough zip Luda would receive.

For each of the 17 changes, this script:
  1. Reports the screenshot's file size (so identical sizes = duplicates)
  2. Navigates to the live URL the card links to
  3. Reports what page (h1, key text) the user lands on
  4. Cross-checks whether the URL destination matches what the card describes

Outputs a single audit table so we can spot mismatches before sending.
"""

import asyncio
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
HTML_PATH = ROOT / "docs" / "walkthrough_report" / "WALKTHROUGH.html"
SCREENSHOTS_DIR = ROOT / "docs" / "walkthrough_report" / "screenshots"

# Pull each card's id, title, url, click_tab from the rendered HTML.
TEXT_PROBES = [
    "Top 5 Skills for the Targeted Role",
    "Targeted Role",
    "Detected role",
    "Continue to Learning Path",
    "Define Your Target",
    "Analysis Complete",
    "Ready to Start",
    "AI Learning Path",
    "Personalize your agent",
    "Implementation Task",
    "Run in ChatGPT",
    "Assignment",
    "Concepts",
    "Example 1",
    "Example 2",
]


def parse_html_cards() -> list[dict]:
    """Extract per-card metadata from the rendered HTML, including the tab name
    a reviewer is told to click (if any)."""
    text = HTML_PATH.read_text(encoding="utf-8")
    cards = []
    # Each card is a self-contained div block; capture id, title, url, and the
    # "click X tab" hint from the to-see strip. Use a lookahead so consecutive
    # card markers can both be matched.
    card_pattern = re.compile(
        r'<div class="card" id="change-([^"]+)"[^>]*?>(.*?)(?=<div class="card" id="change-)',
        re.DOTALL,
    )
    full = text + '<div class="card" id="change-END"'
    for m in card_pattern.finditer(full):
        cid = m.group(1)
        block = m.group(2)
        title_m = re.search(r"<h2>([^<]+)</h2>", block)
        url_m = re.search(r'<a href="([^"]+)" target="_blank" class="url"', block)
        tab_m = re.search(r"click ([A-Z][\w\s]*?) tab", block)
        cards.append({
            "id": cid,
            "title": (title_m.group(1) if title_m else cid).strip(),
            "url": url_m.group(1) if url_m else "",
            "click_tab": tab_m.group(1).strip() if tab_m else None,
        })
    return cards


async def probe_url(page, url: str, click_tab: str | None = None) -> dict:
    """Navigate, optionally click a tab, then report content."""
    info = {"target": url, "final": None, "h1": None, "found": [], "tab_clicked": click_tab}
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(6000)
        if click_tab:
            try:
                btn = await page.query_selector(f'button:has-text("{click_tab}")')
                if btn:
                    await btn.click()
                    await page.wait_for_timeout(1500)
                else:
                    info["tab_warning"] = f"no button matched '{click_tab}'"
            except Exception as e:
                info["tab_warning"] = str(e)[:60]
        info["final"] = page.url
        info["h1"] = (await page.evaluate("() => document.querySelector('h1')?.textContent || ''")).strip()[:80]
        body = await page.evaluate("() => document.body.textContent || ''")
        for probe in TEXT_PROBES:
            if probe in body:
                info["found"].append(probe)
    except Exception as e:
        info["error"] = str(e)[:80]
    return info


async def main():
    if not HTML_PATH.exists():
        sys.exit(f"WALKTHROUGH.html not found at {HTML_PATH}")

    cards = parse_html_cards()
    print(f"Parsed {len(cards)} cards from HTML.\n")

    # Phase 1: file-size duplicates
    print("=" * 80)
    print("STEP 1 - Screenshot uniqueness")
    print("=" * 80)
    sizes = {}
    for c in cards:
        path = SCREENSHOTS_DIR / f"{c['id']}.png"
        if path.exists():
            sz = path.stat().st_size
            sizes.setdefault(sz, []).append(c["id"])
    duplicates = {sz: ids for sz, ids in sizes.items() if len(ids) > 1}
    if duplicates:
        for sz, ids in duplicates.items():
            print(f"  DUPLICATE size {sz}: {ids}")
    else:
        print("  All screenshots have distinct file sizes.")
    print()

    # Phase 2: URL destination probes
    print("=" * 80)
    print("STEP 2 - URL destinations (Playwright)")
    print("=" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1100})

        # Probe each card individually since tab clicks differ per card.
        results = {}
        for c in cards:
            key = (c["url"], c.get("click_tab"))
            if key in results:
                continue
            print(f"\nProbing card {c['id']}: {c['url']} (tab: {c.get('click_tab')})")
            r = await probe_url(page, c["url"], c.get("click_tab"))
            results[key] = r
            print(f"  Final URL:  {r.get('final')}")
            print(f"  H1:         {r.get('h1')}")
            print(f"  Probes hit: {', '.join(r.get('found', [])) or '(none)'}")
            if r.get("error"):
                print(f"  ERROR:      {r['error']}")
            if r.get("tab_warning"):
                print(f"  TAB WARN:   {r['tab_warning']}")

        await browser.close()

    # Phase 3: per-card audit
    print("\n" + "=" * 80)
    print("STEP 3 - Per-card audit (does URL destination match card description?)")
    print("=" * 80)
    expectations = {
        "01_homepage_simplified": {"requires_h1_contains": "AI", "redirect_ok": True},
        "02_profiles_copy": {"requires_h1_contains": ""},
        "03_skills_review_merged": {"requires_text": "Top 5 Skills for the Targeted Role"},
        "04_skill_hover_tooltip": {"requires_text": "Top 5 Skills for the Targeted Role"},
        "05_targeted_role_label": {"requires_text": "Targeted Role"},
        "06_skill_match_messaging": {"requires_text": "Top 5 Skills for the Targeted Role"},
        "07_learning_dashboard_no_gate": {"requires_text": "AI Learning Path"},
        "08_journey_roadmap_removed": {"requires_text": "Continue to Learning Path"},
        "09_chapter_section_nav": {"requires_text": "Assignment"},
        "10_chapter_title_ontology_name": {"requires_h1_contains": ""},
        "11_concepts_with_mnemonic": {"requires_text": "Concepts"},
        "12_example1_steps_array": {"requires_text": "Example 1"},
        "13_example2_ab_comparison": {"requires_text": "Example 2"},
        "14_agent_build_section": {"requires_text": "Personalize your agent"},
        "15_try_in_llm_buttons": {"requires_text": "Run in ChatGPT"},
        "16_implementation_task_section": {"requires_text": "Implementation Task"},
        "17_deterministic_skill_ordering": {"requires_text": "Top 5 Skills for the Targeted Role"},
    }
    print(f"\n{'ID':40} {'URL OK':8} {'TEXT OK':10} {'TAB':12} NOTES")
    print("-" * 110)
    for c in cards:
        key = (c["url"], c.get("click_tab"))
        r = results.get(key, {})
        exp = expectations.get(c["id"], {})
        found = r.get("found", [])
        url_ok = "yes" if r.get("final") and not r.get("error") else "NO"
        tab_str = c.get("click_tab") or "-"
        required = exp.get("requires_text")
        text_ok = "n/a"
        note = ""
        if required:
            text_ok = "yes" if required in found else "NO"
            if text_ok == "NO":
                note = f'expected "{required}" not found'
        if r.get("tab_warning"):
            note = (note + f" (tab: {r['tab_warning']})").strip()
        print(f"{c['id']:40} {url_ok:8} {text_ok:10} {tab_str:12} {note}")


if __name__ == "__main__":
    asyncio.run(main())
