"""Verify the chapter disclosure panel + sources renders on a lesson page."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


BASE = "http://95.216.199.47:3000"
OUT_BASE = Path(__file__).resolve().parents[2] / "docs" / "preflight"


def main(path_id: str, lesson_id: str) -> int:
    out_dir = OUT_BASE / "disclosure"
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg = browser.new_page(viewport={"width": 1400, "height": 1000})
        pg.goto(f"{BASE}/learn/{path_id}/lesson/{lesson_id}", wait_until="load")
        # Wait for lesson + disclosure to render
        try:
            pg.wait_for_function(
                "() => /AI-generated lesson/.test(document.body.innerText)",
                timeout=60000,
            )
        except Exception:
            pg.screenshot(path=str(out_dir / "disclosure_missing.png"), full_page=True)
            print("FAIL: disclosure banner did not appear on lesson page")
            return 1
        pg.wait_for_timeout(800)

        body = pg.locator("body").text_content() or ""
        if "AI-generated lesson" not in body:
            print("FAIL: banner text missing")
            return 1
        if "GenAI Skills Ontology v2.0" not in body:
            print("FAIL: ontology name missing")
            return 1
        print("OK - disclosure banner visible (collapsed)")
        pg.screenshot(path=str(out_dir / "disclosure_collapsed.png"), full_page=False)

        # Expand sources
        try:
            pg.get_by_text("Show sources this chapter was grounded in").click(timeout=10000)
        except Exception:
            print("FAIL: could not click sources expander")
            return 1
        pg.wait_for_timeout(800)
        body_open = pg.locator("body").text_content() or ""
        required = [
            "Skill",
            "Level progression",
            "Where you are now",
            "Where you are headed",
            "exact ontology text",
        ]
        missing = [s for s in required if s not in body_open]
        if missing:
            pg.screenshot(path=str(out_dir / "disclosure_expanded_fail.png"), full_page=True)
            print(f"FAIL: expanded panel missing sections: {missing}")
            return 1
        pg.screenshot(path=str(out_dir / "disclosure_expanded.png"), full_page=True)
        print(f"OK - sources panel contains all {len(required)} required sections")
        browser.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: verify_chapter_disclosure.py <path_id> <lesson_id>")
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
