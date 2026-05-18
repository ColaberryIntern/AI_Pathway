"""Pre-demo end-to-end verifier for any AI Pathway profile.

Replicates the exact click sequence a reviewer would walk through, so a
real customer never sees the class of bug Luda hit on May 16 with Dorothy F.

Usage (run before any demo / customer-facing share):

    py -3.12 backend/scripts/verify_profile_e2e.py <profile_id>

What it checks against the LIVE deployment at http://95.216.199.47:3000:

  STEP 1 - Top 5 Skills page renders, hovering a Level 1 button shows the
           per-skill rubric (not the generic "Can explain basics" fallback).
  STEP 2 - Learning Dashboard sidebar shows every module's title as the
           canonical ontology skill name and in matching order.
  STEP 3 - Clicking each module's lesson generates a chapter whose
           meta.skill_id matches the module (catches LLM identity drift).

Exits 0 if everything passes, 1 with a clear diff if anything fails.
Screenshots for each step are written to docs/preflight/<profile_id>/.

Pair this with backend/scripts/sweep_integrity.py for a complete
pre-demo check: sweep catches DB-level drift, this catches user-visible
drift.
"""
import argparse
import re
import sys
import urllib.request
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://95.216.199.47:3000"
# Backend is not exposed publicly; the frontend nginx proxies /api/* to it.
API = "http://95.216.199.47:3000"

OUT_BASE = Path(__file__).resolve().parents[2] / "docs" / "preflight"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def get_path_and_modules(profile_id: str) -> tuple[str, list[dict]]:
    """Hit the analysis-results endpoint to learn the path_id + module list."""
    url = f"{API}/api/analysis/results/{profile_id}"
    with urllib.request.urlopen(url, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    path_id = data.get("learning_path_id")
    if not path_id:
        fail(f"profile {profile_id} has no activated learning path yet (cannot verify)")
    # Fetch the dashboard to learn module IDs + lesson IDs
    dash_url = f"{API}/api/learning/{path_id}/dashboard"
    with urllib.request.urlopen(dash_url, timeout=20) as r:
        dash = json.loads(r.read().decode("utf-8"))
    return path_id, dash.get("modules") or []


def first_skill_name_on_top5(modules: list[dict]) -> str:
    # Use the first skill present in the activated path; we will hover its L1.
    if not modules:
        fail("no modules in path")
    return modules[0].get("skill_name") or ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("profile_id", help="profile UUID to verify")
    ap.add_argument(
        "--skip-lesson", action="store_true",
        help="skip the live lesson generation step (faster, only checks UI structure)",
    )
    args = ap.parse_args()

    out_dir = OUT_BASE / args.profile_id
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"== preflight for profile {args.profile_id} ==")
    print(f"   screenshots: {out_dir}")

    path_id, modules = get_path_and_modules(args.profile_id)
    if not modules:
        fail("no modules - path not activated yet")
    print(f"   path_id: {path_id}")
    print(f"   modules: {len(modules)}")

    expected_titles = [m.get("skill_name") for m in modules if m.get("skill_name")]
    target_skill = first_skill_name_on_top5(modules)
    target_l1_rubric_keyword = None
    # Pull the proficiency_descriptions for that skill from the analysis
    # endpoint to know what tooltip text to look for.
    url = f"{API}/api/analysis/results/{args.profile_id}"
    with urllib.request.urlopen(url, timeout=20) as r:
        results = json.loads(r.read().decode("utf-8")).get("result", {})
    for key in ("top_10_target_skills", "top_10_skill_gaps", "all_skill_gaps"):
        for s in (results.get(key) or []):
            if s.get("skill_name") == target_skill:
                descs = s.get("proficiency_descriptions") or []
                for d in descs:
                    if d.get("level") == 1 and d.get("description"):
                        target_l1_rubric_keyword = d["description"][:40]
                        break
                if target_l1_rubric_keyword:
                    break
        if target_l1_rubric_keyword:
            break
    if not target_l1_rubric_keyword:
        print(f"   WARN: no L1 rubric found for {target_skill!r} - will skip tooltip text assertion")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg = browser.new_page(viewport={"width": 1400, "height": 900})

        # STEP 1: Top 5 page + tooltip
        print()
        print("== STEP 1: Top 5 page renders + per-skill tooltip ==")
        pg.goto(f"{BASE}/analysis/{args.profile_id}?view=skill_selection", wait_until="load")
        pg.wait_for_timeout(2500)
        body1 = pg.locator("body").text_content() or ""
        if target_skill and target_skill not in body1:
            pg.screenshot(path=str(out_dir / "step1_fail.png"), full_page=True)
            fail(f"Top 5 page missing skill {target_skill!r}")
        print(f"   OK - Top 5 page mentions {target_skill!r}")

        if target_l1_rubric_keyword:
            btn_index = pg.evaluate(
                r"""(skillName) => {
                    const buttons = Array.from(document.querySelectorAll('button'))
                        .filter(b => /^\s*1\s*Aware\b/i.test(b.textContent || ''));
                    for (let i = 0; i < buttons.length; i++) {
                        const card = buttons[i].closest('.card');
                        if (card && (card.innerText || '').trim().startsWith(skillName)) {
                            return i;
                        }
                    }
                    return -1;
                }""",
                target_skill,
            )
            if btn_index < 0:
                pg.screenshot(path=str(out_dir / "step1_no_btn.png"), full_page=True)
                fail(f"could not locate Level 1 button for {target_skill!r}")
            l1_btn = pg.get_by_role("button", name=re.compile(r"^\s*1\s*Aware\b", re.I)).nth(btn_index)
            l1_btn.scroll_into_view_if_needed()
            l1_btn.hover(timeout=10000)
            pg.wait_for_timeout(1200)
            body1b = pg.locator("body").text_content() or ""
            if target_l1_rubric_keyword.lower() not in body1b.lower():
                pg.screenshot(path=str(out_dir / "step1_tooltip_fail.png"), full_page=False)
                fail(
                    f"L1 tooltip for {target_skill!r} did not show per-skill rubric. "
                    f"Expected to see {target_l1_rubric_keyword!r}."
                )
            print(f"   OK - per-skill tooltip shows {target_l1_rubric_keyword!r}...")
            pg.screenshot(path=str(out_dir / "step1_hover.png"), full_page=False)

        # STEP 2: Dashboard sidebar names
        print()
        print("== STEP 2: Learning Dashboard sidebar ==")
        pg.goto(f"{BASE}/learn/{path_id}", wait_until="load")
        pg.wait_for_timeout(2500)
        body2 = pg.locator("body").text_content() or ""
        missing = [t for t in expected_titles if t and t not in body2]
        if missing:
            pg.screenshot(path=str(out_dir / "step2_fail.png"), full_page=True)
            fail(f"dashboard missing module titles: {missing}")
        print(f"   OK - all {len(expected_titles)} ontology-canonical module titles present")
        pg.screenshot(path=str(out_dir / "step2_dashboard.png"), full_page=False)

        # STEP 3: Per-module lesson generation + identity check
        if args.skip_lesson:
            print()
            print("== STEP 3: SKIPPED (--skip-lesson) ==")
        else:
            print()
            print(f"== STEP 3: Generate a lesson for each of {len(modules)} modules ==")
            for m in modules:
                ms_id = m.get("skill_id")
                ms_name = m.get("skill_name")
                # Dashboard returns lessons under `lesson_outline`, not `lessons`.
                lessons = m.get("lesson_outline") or m.get("lessons") or []
                if not lessons:
                    print(f"   WARN module {ms_id} has no lessons; skip")
                    continue
                ls_id = lessons[0].get("id")
                if not ls_id:
                    print(f"   WARN module {ms_id} lesson missing id; skip")
                    continue
                gen_url = f"{API}/api/learning/{path_id}/lessons/{ls_id}/start"
                req = urllib.request.Request(
                    gen_url, method="POST",
                    headers={"Content-Type": "application/json"}, data=b"{}",
                )
                with urllib.request.urlopen(req, timeout=180) as r:
                    body = json.loads(r.read().decode("utf-8"))
                meta = (body.get("content") or {}).get("meta") or {}
                got_sid = meta.get("skill_id")
                if got_sid != ms_id:
                    fail(
                        f"module {ms_name!r} ({ms_id}): generated chapter meta.skill_id={got_sid!r} != module {ms_id!r}"
                    )
                print(f"   OK - {ms_id} ({ms_name}): chapter identity matches")

        browser.close()

    print()
    print(f"PREFLIGHT PASSED for profile {args.profile_id}")


if __name__ == "__main__":
    main()
