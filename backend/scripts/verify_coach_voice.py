"""Verify coach intro + outro render on lesson page."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


BASE = "http://95.216.199.47:3000"
OUT_BASE = Path(__file__).resolve().parents[2] / "docs" / "preflight"


def main(path_id: str, lesson_id: str) -> int:
    out_dir = OUT_BASE / "coach"
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg = browser.new_page(viewport={"width": 1400, "height": 1400})
        pg.goto(f"{BASE}/learn/{path_id}/lesson/{lesson_id}", wait_until="load")
        try:
            pg.wait_for_function(
                "() => /Let.s work on/.test(document.body.innerText)",
                timeout=60000,
            )
        except Exception:
            pg.screenshot(path=str(out_dir / "coach_missing.png"), full_page=True)
            print("FAIL: coach intro did not render")
            return 1
        pg.wait_for_timeout(800)
        body = pg.locator("body").text_content() or ""
        checks = [
            ("coach intro greeting", "Let’s work on"),
            ("coach intro tone", "Take about 15 minutes"),
            ("coach outro", "Nice work getting through this chapter"),
            ("coach outro support", "I’ll suggest a smaller first step"),
        ]
        missing = [name for name, needle in checks if needle not in body]
        if missing:
            pg.screenshot(path=str(out_dir / "coach_fail.png"), full_page=True)
            print(f"FAIL: coach voice missing: {missing}")
            return 1
        pg.screenshot(path=str(out_dir / "coach_ok.png"), full_page=True)
        print(f"OK - coach intro + outro both present ({len(checks)} checks)")
        browser.close()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: verify_coach_voice.py <path_id> <lesson_id>")
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
