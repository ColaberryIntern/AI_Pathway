"""Verify the path summary page renders with skills, next steps, retake date."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


BASE = "http://95.216.199.47:3000"
OUT_BASE = Path(__file__).resolve().parents[2] / "docs" / "preflight"


def main(path_id: str) -> int:
    out_dir = OUT_BASE / "summary"
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg = browser.new_page(viewport={"width": 1400, "height": 1400})
        pg.goto(f"{BASE}/learn/{path_id}/complete", wait_until="load")
        try:
            pg.wait_for_function(
                "() => /What you can now do|Pathway complete|progress so far/.test(document.body.innerText)",
                timeout=30000,
            )
        except Exception:
            pg.screenshot(path=str(out_dir / "summary_missing.png"), full_page=True)
            print("FAIL: summary page did not render")
            return 1
        pg.wait_for_timeout(800)
        body = pg.locator("body").text_content() or ""
        checks = [
            "What you can now do",
            "Where to take this next",
            "Come back in 60 days",
            "Start another pathway",
        ]
        missing = [s for s in checks if s not in body]
        if missing:
            pg.screenshot(path=str(out_dir / "summary_fail.png"), full_page=True)
            print(f"FAIL: missing sections: {missing}")
            return 1
        pg.screenshot(path=str(out_dir / "summary_ok.png"), full_page=True)
        print(f"OK - all {len(checks)} summary sections present")
        browser.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: verify_path_summary.py <path_id>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
