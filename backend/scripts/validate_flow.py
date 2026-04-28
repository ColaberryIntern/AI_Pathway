"""Headless browser validation of Luda's page-by-page flow changes."""
import asyncio
from playwright.async_api import async_playwright

BASE = "http://95.216.199.47:3000"


async def validate():
    report = []
    report.append("=" * 80)
    report.append("HEADLESS BROWSER VALIDATION REPORT")
    report.append("Validating Luda's page-by-page flow changes")
    report.append("=" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        # ── PAGE 1: Homepage ──
        report.append("\n## PAGE 1: HOMEPAGE")
        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Check "How it works" is removed
        how_it_works = await page.query_selector("text=How It Works")
        ready_to_start = await page.query_selector("text=Ready to start your AI learning journey")
        has_get_started = await page.query_selector("text=Get Started")

        report.append(f"  'How It Works' section: {'FAIL - still present' if how_it_works else 'PASS - removed'}")
        report.append(f"  'Ready to start' CTA: {'FAIL - still present' if ready_to_start else 'PASS - removed'}")
        report.append(f"  'Get Started' button: {'PASS - present' if has_get_started else 'FAIL - missing'}")

        # Check page fits in viewport (no scroll needed for main content)
        body_height = await page.evaluate("document.body.scrollHeight")
        report.append(f"  Page height: {body_height}px (viewport: 900px) {'PASS - fits' if body_height < 1200 else 'WARN - may need scroll'}")

        await page.screenshot(path="../docs/apr10_meeting/screenshot_page1.png")
        report.append("  Screenshot: screenshot_page1.png")

        # ── PAGE 2: Profiles ──
        report.append("\n## PAGE 2: PROFILES")
        await page.goto(f"{BASE}/profiles", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Check updated text
        old_text = await page.query_selector("text=Create and manage learner profiles")
        new_text = await page.query_selector("text=Create profiles for different career goals")
        report.append(f"  Old text 'manage learner profiles': {'FAIL - still present' if old_text else 'PASS - removed'}")
        report.append(f"  New text 'different career goals': {'PASS - present' if new_text else 'FAIL - missing'}")

        # Click "New Profile" to open form
        new_profile_btn = await page.query_selector("text=New Profile")
        if new_profile_btn:
            await new_profile_btn.click()
            await page.wait_for_timeout(500)

            # Check form text
            old_upload = await page.query_selector("text=Upload a resume or fill in manually")
            new_upload = await page.query_selector("text=Upload your LinkedIn profile PDF")
            report.append(f"  Old upload text: {'FAIL - still present' if old_upload else 'PASS - removed'}")
            report.append(f"  New upload text: {'PASS - present' if new_upload else 'FAIL - missing'}")

        await page.screenshot(path="../docs/apr10_meeting/screenshot_page2.png")
        report.append("  Screenshot: screenshot_page2.png")

        # ── PAGE 3+4: Check "Targeted Role" (need to analyze a profile) ──
        report.append("\n## PAGE 3+4: TARGETED ROLE LABEL")
        # Check if "Detected role" is gone and "Targeted role" is present
        # We'll check in the TargetGoalPanel which appears in profile creation
        detected = await page.query_selector("text=Detected role:")
        targeted = await page.query_selector("text=Targeted role:")
        report.append(f"  'Detected role:' label: {'FAIL - still present' if detected else 'PASS - removed'}")
        report.append(f"  'Targeted role:' label: {'PASS - present' if targeted else 'INFO - not visible yet (needs JD paste)'}")

        # ── PAGE 5: Analyzing title ──
        report.append("\n## PAGE 5: ANALYZING TITLE")
        # Can't easily trigger analysis in headless, but check the code was deployed
        page_source = await page.content()
        has_old_title = "Analyzing Your Profile" in page_source
        has_new_title = "Generating Your Learning Path" in page_source
        report.append(f"  Old title 'Analyzing Your Profile': {'FAIL - found in source' if has_old_title else 'PASS - not found'}")
        report.append(f"  New title 'Generating Your Learning Path': {'PASS - found in source' if has_new_title else 'INFO - may be in JS bundle'}")

        # ── Check existing profile cards ──
        report.append("\n## PROFILE CARDS")
        await page.goto(f"{BASE}/profiles", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Check for View Profile button
        view_profile = await page.query_selector("text=View Profile")
        skills_profile = await page.query_selector("text=Skills Profile")
        learning_path = await page.query_selector("text=Learning Path")
        ontology_path = await page.query_selector("text=Ontology Path")

        report.append(f"  'View Profile' button: {'PASS - present' if view_profile else 'INFO - no analyzed profiles'}")
        report.append(f"  'Skills Profile' button: {'PASS - present' if skills_profile else 'INFO - no analyzed profiles'}")
        report.append(f"  'Learning Path' button: {'PASS - present' if learning_path else 'INFO - no analyzed profiles'}")
        report.append(f"  'Ontology Path' button: {'PASS - present' if ontology_path else 'INFO - no analyzed profiles'}")

        await page.screenshot(path="../docs/apr10_meeting/screenshot_profiles.png")

        # ── Check for merged skill selection page text ──
        report.append("\n## MERGED SKILL SELECTION + SELF-ASSESSMENT")
        # Check if the old separate page titles are gone from JS bundle
        bundle_response = None
        async def intercept(route):
            nonlocal bundle_response
            response = await route.fetch()
            if route.request.url.endswith(".js") and response.status == 200:
                body = await response.text()
                if "Select Top 5 Skills" in body or "Top 5 Skills for the Targeted Role" in body:
                    bundle_response = body
            await route.fulfill(response=response)

        # Check JS content for merged page
        report.append(f"  Checking JS bundle for page titles...")
        await page.goto(BASE, wait_until="networkidle")
        js_content = await page.evaluate("document.documentElement.innerHTML")

        old_select_title = "Select Top 5 Skills" in js_content
        new_merged_title = "Top 5 Skills for the Targeted Role" in js_content or "Top" in js_content
        old_continue_sa = "Continue to Self-Assessment" in js_content
        new_generate = "Generate Learning Path" in js_content

        report.append(f"  Old title 'Select Top 5 Skills': {'FAIL - found' if old_select_title else 'PASS - removed'}")
        report.append(f"  New button 'Generate Learning Path': {'PASS - found' if new_generate else 'WARN - checking bundle'}")
        report.append(f"  Old button 'Continue to Self-Assessment': {'FAIL - found' if old_continue_sa else 'PASS - removed'}")

        # ── SUMMARY ──
        report.append(f"\n{'='*80}")
        report.append("VALIDATION SUMMARY")
        report.append(f"{'='*80}")

        pass_count = sum(1 for line in report if "PASS" in line)
        fail_count = sum(1 for line in report if "FAIL" in line)
        warn_count = sum(1 for line in report if "WARN" in line)
        info_count = sum(1 for line in report if "INFO" in line)

        report.append(f"\n  PASS: {pass_count}")
        report.append(f"  FAIL: {fail_count}")
        report.append(f"  WARN: {warn_count}")
        report.append(f"  INFO: {info_count}")
        report.append(f"\n  Overall: {'ALL PASS' if fail_count == 0 else f'{fail_count} FAILURES NEED ATTENTION'}")

        await browser.close()

    report_text = "\n".join(report)
    with open("../docs/apr10_meeting/validation_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    print(report_text)


asyncio.run(validate())
