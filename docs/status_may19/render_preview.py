"""Render the STATUS_MAY19.html in headless Chromium and capture
section-by-section screenshots so the user can verify before sending.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "docs" / "status_may19" / "STATUS_MAY19.html"
OUT = ROOT / "docs" / "status_may19"


def main() -> None:
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1100, "height": 1000})
        pg.goto(f"file:///{HTML.as_posix()}", wait_until="load")
        pg.wait_for_timeout(800)
        # Full-page render
        pg.screenshot(path=str(OUT / "preview_full.png"), full_page=True)
        # Top of the document
        pg.screenshot(path=str(OUT / "preview_top.png"), full_page=False, clip={"x": 0, "y": 0, "width": 1100, "height": 1000})
        # Outstanding section: scroll to the H2 "Outstanding items still open"
        pg.evaluate("""
            () => {
                const headings = Array.from(document.querySelectorAll('h2'));
                const target = headings.find(h => /Outstanding items still open/i.test(h.textContent || ''));
                if (target) target.scrollIntoView({ block: 'start' });
            }
        """)
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / "preview_outstanding.png"), full_page=False)
        b.close()
    print("Wrote previews to docs/status_may19/preview_*.png")


if __name__ == "__main__":
    main()
