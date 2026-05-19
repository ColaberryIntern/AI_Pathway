"""Verify the ontology narrative panel renders correctly on the Top 5 page
for a given profile. Loads the page in headless Chromium, clicks the
expander, and confirms each required section is visible.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


BASE = "http://95.216.199.47:3000"
OUT_BASE = Path(__file__).resolve().parents[2] / "docs" / "preflight"


def main(profile_id: str) -> int:
    out_dir = OUT_BASE / profile_id
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg = browser.new_page(viewport={"width": 1400, "height": 1000})
        pg.goto(f"{BASE}/analysis/{profile_id}?view=skill_selection", wait_until="load")
        pg.wait_for_timeout(2500)

        body = pg.locator("body").text_content() or ""
        if "How do I know these are the right skills?" not in body:
            pg.screenshot(path=str(out_dir / "narrative_missing.png"), full_page=True)
            print("FAIL: narrative summary line not found on Top 5 page")
            return 1
        print("OK - narrative summary line is visible (collapsed state)")
        pg.screenshot(path=str(out_dir / "narrative_collapsed.png"), full_page=False)

        # Click the expander
        try:
            pg.get_by_text("How do I know these are the right skills?").click(timeout=10000)
        except Exception:
            print("FAIL: could not click narrative expander")
            return 1
        pg.wait_for_timeout(1000)
        body_open = pg.locator("body").text_content() or ""
        required_substrings = [
            "Detected role family",
            "Scoring rubric",
            "Importance",
            "Breadth",
            "Momentum",
            "Connectivity",
            "Career Signal",
            "Diversity rule",
        ]
        missing = [s for s in required_substrings if s not in body_open]
        if missing:
            pg.screenshot(path=str(out_dir / "narrative_expanded_fail.png"), full_page=True)
            print(f"FAIL: expanded narrative missing sections: {missing}")
            return 1
        pg.screenshot(path=str(out_dir / "narrative_expanded.png"), full_page=True)
        print(f"OK - expanded narrative contains all {len(required_substrings)} required sections")
        browser.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: verify_ontology_narrative.py <profile_id>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
