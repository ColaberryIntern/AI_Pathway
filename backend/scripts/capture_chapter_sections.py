"""Click through each chapter section tab and screenshot. Reuses an existing
profile + path + lesson rather than regenerating.

Run after e2e_screenshot_report.py if you want better per-section captures.
"""
import asyncio
import sys
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

BASE = "http://95.216.199.47:3000"
API = f"{BASE}/api"
SCREENSHOT_DIR = Path(__file__).parent.parent.parent / "docs" / "apr30_e2e_report"


async def main():
    # Find a profile with an active chapter
    print("Finding existing profile with chapter...")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{API}/profiles/")
        profiles = r.json()

        # Pick a profile with has_learning_path=True
        target = None
        for p in profiles:
            if p.get("has_learning_path") and p.get("learning_path_id"):
                # Get its dashboard to find a lesson
                r2 = await client.get(f"{API}/learning/{p['learning_path_id']}/dashboard")
                if r2.status_code == 200:
                    dash = r2.json()
                    modules = dash.get("modules", [])
                    if modules:
                        outline = modules[0].get("lesson_outline", [])
                        if outline:
                            target = {
                                "profile_id": p["id"],
                                "name": p["name"],
                                "path_id": p["learning_path_id"],
                                "lesson_id": outline[0].get("id"),
                            }
                            break

    if not target:
        print("No profile with active chapter found. Run e2e_screenshot_report.py first.")
        sys.exit(1)

    print(f"Using: {target['name']}")
    print(f"  path: {target['path_id']}")
    print(f"  lesson: {target['lesson_id']}")

    chapter_url = f"{BASE}/learn/{target['path_id']}/lesson/{target['lesson_id']}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1100})

        print(f"\nNavigating to chapter: {chapter_url}")
        await page.goto(chapter_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Capture each section by clicking the tab
        tabs = ["Scenario", "Concepts", "Example 1", "Example 2", "Build", "Assignment"]
        for i, label in enumerate(tabs, 1):
            print(f"  Capturing section {i}: {label}")
            try:
                # Click the tab
                tab = await page.query_selector(f'button:has-text("{label}")')
                if not tab:
                    tab = await page.query_selector(f'text="{label}"')
                if tab:
                    await tab.click()
                    await page.wait_for_timeout(1500)
                    # Take a full-page screenshot of just the chapter content
                    safe_label = label.lower().replace(" ", "_")
                    await page.screenshot(
                        path=str(SCREENSHOT_DIR / f"section_{i}_{safe_label}.png"),
                        full_page=True,
                    )
                else:
                    print(f"    tab not found")
            except Exception as e:
                print(f"    failed: {e}")

        # Take the full chapter screenshot one more time for completeness
        print("  Capturing full chapter")
        # Click first tab to reset
        try:
            first_tab = await page.query_selector('button:has-text("Scenario")')
            if first_tab:
                await first_tab.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass
        await page.screenshot(
            path=str(SCREENSHOT_DIR / "chapter_overview.png"),
            full_page=True,
        )

        await browser.close()

    print(f"\nDone. Screenshots in {SCREENSHOT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
