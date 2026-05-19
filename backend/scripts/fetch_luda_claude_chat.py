"""Pull the full text of Luda's shared Claude conversation about
Halyna Mushak. The /share/ URL is a SPA so a plain HTTP fetch returns
only "Claude" - load it in headless Chromium so React can render the
transcript, then dump the entire body text to disk.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://claude.ai/share/15c53368-8743-47f8-9ca4-69866fb7f387"
OUT = Path(__file__).resolve().parents[2] / "docs" / "luda_may19" / "halyna_claude_chat.txt"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        pg = ctx.new_page()
        pg.goto(URL, wait_until="load")
        # Share pages render conversation lazily - give the SPA up to 30s
        # to fetch and render, polling until a substantial amount of text
        # is visible.
        try:
            pg.wait_for_function(
                "() => (document.body.innerText || '').length > 2000",
                timeout=30000,
            )
        except Exception:
            pass
        pg.wait_for_timeout(2000)
        text = pg.locator("body").inner_text() or ""
        OUT.write_text(text, encoding="utf-8")
        print(f"Wrote {len(text)} chars to {OUT}")
        # Also screenshot so we can sanity-check what was rendered.
        pg.screenshot(path=str(OUT.with_suffix(".png")), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
