"""Headless browser verification of WALKTHROUGH.html with 7-card filter."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parents[2] / "docs" / "walkthrough_report" / "WALKTHROUGH.html"

EXPECTED_IDS = [
    "18_skill_rank_sequential",
    "19_dashboard_back_to_skill_review",
    "20_rating_persistence",
    "21_per_skill_hover_descriptions",
    "22_item_06_status_deferred",
    "23_item_14_status_queued",
    "24_item_17_status_needs_clarification",
]

CONTENT_CHECKS = [
    "Top 5 Skills",
    "Back to skill review",
    "localStorage",
    "Practitioner",
    "Deferred",
    "Queued",
    "Clarification",
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(f"file:///{HTML.as_posix()}", wait_until="load")
        # Wait for all images to finish decoding (data URIs load synchronously
        # but lazy-loaded images need a scroll trigger).
        page.evaluate("""
            async () => {
                const imgs = Array.from(document.querySelectorAll('img'));
                imgs.forEach(i => { i.loading = 'eager'; });
                await Promise.all(imgs.map(i => {
                    if (i.complete && i.naturalWidth > 0) return Promise.resolve();
                    return new Promise(res => {
                        i.addEventListener('load', res, { once: true });
                        i.addEventListener('error', res, { once: true });
                    });
                }));
            }
        """)
        page.wait_for_timeout(500)

        body_text = page.locator("body").text_content() or ""
        images = page.locator("img").all()
        loaded = 0
        broken = []
        for i, img in enumerate(images):
            nw = img.evaluate("el => el.naturalWidth")
            nh = img.evaluate("el => el.naturalHeight")
            if nw and nw > 0 and nh > 0:
                loaded += 1
            else:
                alt = img.get_attribute("alt") or ""
                broken.append(f"#{i} {alt}")

        print(f"Images total: {len(images)}  loaded: {loaded}  broken: {len(broken)}")
        if broken:
            for b in broken:
                print(f"  BROKEN: {b}")

        print("\nID anchors present (each card has an id attribute):")
        for cid in EXPECTED_IDS:
            found = page.locator(f'[id="{cid}"], [id="change-{cid}"]').count() > 0
            print(f"  {'OK ' if found else 'MISS'} - {cid}")

        print("\nContent checks:")
        for c in CONTENT_CHECKS:
            found = c.lower() in body_text.lower()
            print(f"  {'OK ' if found else 'MISS'} - {c}")

        screenshot_path = HTML.parent / "verify_7cards_top.png"
        page.screenshot(path=str(screenshot_path), full_page=False)
        print(f"\nScreenshot: {screenshot_path}")
        browser.close()


if __name__ == "__main__":
    main()
