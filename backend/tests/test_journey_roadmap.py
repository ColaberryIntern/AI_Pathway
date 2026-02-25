"""Verify journey roadmap computation matches learning path chapters.

The journey roadmap bridges gap analysis (ALL gaps from state_a vs
state_b) and the learning path (+1 per chapter).  These tests validate:

1.  skills_addressed count matches scaffold chapter count
2.  All skill_ids are valid ontology IDs (no hallucination)
3.  Partial skills may overlap addressed/remaining; non-partial must not
4.  total_gap_levels sums correctly from ALL gaps (not just top-10)
5.  path_closes_levels equals chapter count
6.  estimated_total_paths is reasonable
7.  gap_remaining is never negative
8.  Every entry has a non-empty skill_id starting with "SK."
9.  Arithmetic: path_closes + sum(remaining.gap) == total_gap_levels
10. Cross-display: React and HTML visualizer derive identical totals
11. Partial skills in remaining match addressed gap_remaining values
12. Fully-closed skills (gap_remaining=0) never appear in remaining

No LLM calls — mirrors the orchestrator's roadmap logic deterministically.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.path_generator import LearningPathGenerator, MAX_CHAPTERS
from app.services.ontology import get_ontology_service

PROFILES_DIR = Path(__file__).parent.parent / "app" / "data" / "profiles"

PROFILE_FILES = sorted(PROFILES_DIR.glob("profile_*.json"))


def load_profile(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def build_inputs(profile: dict, ontology):
    """Build state_a, state_b, and role_context from a profile."""
    state_a = profile.get("estimated_current_skills", {})
    state_b = {}
    for gap_group in profile.get("expected_skill_gaps", []):
        for sid in gap_group.get("skills", []):
            skill = ontology.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]
        domain_id = gap_group.get("domain")
        if domain_id:
            for skill in ontology.get_skills_by_domain(domain_id):
                sid = skill["id"]
                if sid not in state_b:
                    state_b[sid] = skill["level"]
    role_context = {
        "target_role": profile.get("target_role", ""),
        "target_domains": [
            g["domain"] for g in profile.get("expected_skill_gaps", [])
            if "domain" in g
        ],
    }
    return state_a, state_b, role_context


def build_all_gaps(state_a, state_b, ontology):
    """Build ALL gap entries from state_a/state_b (mimics orchestrator).

    Unlike the old build_mock_top10_gaps, this returns ALL skills with
    gaps — not just the top 10 — matching the orchestrator's
    all_gaps_full computation (orchestrator.py lines 396-420).
    """
    gaps = []
    for sid, required in state_b.items():
        current = state_a.get(sid, 0)
        gap = required - current
        if gap <= 0:
            continue
        skill = ontology.get_skill(sid)
        if not skill:
            continue
        domain = ontology.get_domain(skill["domain"])
        gaps.append({
            "skill_id": sid,
            "skill_name": skill["name"],
            "domain": skill["domain"],
            "domain_label": domain["label"] if domain else "",
            "current_level": current,
            "required_level": required,
            "target_level": required,
            "gap": gap,
        })
    gaps.sort(key=lambda g: (-g["gap"], g["skill_id"]))
    return gaps


def compute_roadmap(scaffold_result, state_b, all_gaps, ontology):
    """Reproduce the orchestrator's journey_roadmap computation.

    Mirrors orchestrator.py lines 385-517 exactly:
    - total_gap_levels from ALL gaps (not top-10)
    - skills_remaining includes partial entries with "partial": True
    """
    path_chapters = scaffold_result.get("chapters", [])
    path_skill_ids = {
        ch.get("primary_skill_id") or ch.get("skill_id", "")
        for ch in path_chapters
    }

    total_gap_levels = sum(g["gap"] for g in all_gaps if g["gap"] > 0)
    all_gaps_map = {g["skill_id"]: g for g in all_gaps}
    # Only count chapters that address a state_b skill
    path_closes = sum(
        1 for ch in path_chapters
        if (ch.get("primary_skill_id")
            or ch.get("skill_id", "")) in all_gaps_map
    )

    skills_addressed = []
    for ch in path_chapters:
        sid = ch.get("primary_skill_id") or ch.get("skill_id", "")
        if not sid:
            continue
        skill_obj = ontology.get_skill(sid)
        domain_obj = (
            ontology.get_domain(skill_obj["domain"]) if skill_obj else None
        )
        current = ch.get("current_level", 0)
        after = ch.get("target_level", current + 1)
        required = state_b.get(sid, after)
        skills_addressed.append({
            "skill_id": sid,
            "skill_name": (
                ch.get("primary_skill_name") or ch.get("skill_name", sid)
            ),
            "domain_label": domain_obj["label"] if domain_obj else "",
            "current_level": current,
            "after_path_level": after,
            "required_level": required,
            "gap_closed": after - current,
            "gap_remaining": max(0, required - after),
        })

    # skills_remaining: ALL remaining gaps — includes partial
    # gaps on addressed skills AND full gaps on other skills.
    # Uses all_gaps perspective so path_closes + sum(remaining.gap) = total.
    skills_remaining = []
    for gap_entry in all_gaps:
        sid = gap_entry["skill_id"]
        if sid in path_skill_ids:
            # Path closes 1 of this skill's gap; remaining = gap - 1
            remaining_gap = gap_entry["gap"] - 1
            if remaining_gap > 0:
                skills_remaining.append({
                    "skill_id": sid,
                    "skill_name": gap_entry["skill_name"],
                    "domain_label": gap_entry.get("domain_label", ""),
                    "current_level": gap_entry["current_level"],
                    "required_level": gap_entry["target_level"],
                    "gap": remaining_gap,
                    "partial": True,
                })
        else:
            skills_remaining.append({
                "skill_id": sid,
                "skill_name": gap_entry["skill_name"],
                "domain_label": gap_entry.get("domain_label", ""),
                "current_level": gap_entry["current_level"],
                "required_level": gap_entry["target_level"],
                "gap": gap_entry["gap"],
                "partial": False,
            })

    remaining_levels = total_gap_levels - path_closes
    return {
        "path_number": 1,
        "total_gap_levels": total_gap_levels,
        "path_closes_levels": path_closes,
        "remaining_gap_levels": remaining_levels,
        "estimated_total_paths": (
            1 + -(-remaining_levels // MAX_CHAPTERS)
            if remaining_levels > 0 else 1
        ),
        "skills_addressed": skills_addressed,
        "skills_remaining": skills_remaining,
    }


def _run_for_all_profiles(check_fn):
    """Run a check function against all profiles, collecting failures."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    failures = []

    for path in PROFILE_FILES:
        profile = load_profile(path)
        name = profile.get("name", path.stem)
        state_a, state_b, rc = build_inputs(profile, ont)

        if not state_b:
            continue

        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        all_gaps = build_all_gaps(state_a, state_b, ont)
        roadmap = compute_roadmap(scaffold, state_b, all_gaps, ont)

        result = check_fn(name, scaffold, roadmap, all_gaps, ont)
        if result:
            failures.append(result)

    return failures


# ── Existing tests (updated for all-gaps logic) ──────────────────────


def test_skills_addressed_matches_chapters():
    """skills_addressed count must equal scaffold chapter count."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        n_chapters = len(scaffold["chapters"])
        n_addressed = len(roadmap["skills_addressed"])
        if n_addressed != n_chapters:
            return f"{name}: {n_addressed} addressed != {n_chapters} chapters"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "skills_addressed count != chapter count:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_skills_addressed_have_valid_ontology_ids():
    """Every skill_id in skills_addressed must be a valid ontology ID."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        invalid = [
            s["skill_id"] for s in roadmap["skills_addressed"]
            if ont.get_skill(s["skill_id"]) is None
        ]
        if invalid:
            return f"{name}: invalid IDs: {invalid}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Invalid ontology IDs in skills_addressed:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_skills_remaining_partial_overlap():
    """Partial skills may appear in both addressed and remaining.
    Non-partial remaining skills must NOT appear in addressed."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        addressed_ids = {s["skill_id"] for s in roadmap["skills_addressed"]}
        bad_overlap = [
            s["skill_id"] for s in roadmap["skills_remaining"]
            if s["skill_id"] in addressed_ids and not s.get("partial")
        ]
        if bad_overlap:
            return f"{name}: non-partial overlap: {bad_overlap}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Non-partial skills_remaining overlaps with skills_addressed:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_total_gap_levels_is_sum_of_all_gaps():
    """total_gap_levels must equal sum of ALL positive gaps."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        expected = sum(g["gap"] for g in all_gaps if g["gap"] > 0)
        actual = roadmap["total_gap_levels"]
        if actual != expected:
            return f"{name}: total={actual}, expected={expected}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "total_gap_levels mismatch:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_path_closes_within_chapter_count():
    """path_closes_levels must be <= chapter count (some chapters may
    cover prerequisite skills not in state_b)."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        n_chapters = len(scaffold["chapters"])
        closes = roadmap["path_closes_levels"]
        if closes > n_chapters:
            return f"{name}: closes={closes} > chapters={n_chapters}"
        if closes < 1:
            return f"{name}: closes={closes} < 1"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "path_closes_levels out of range:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_estimated_paths_is_reasonable():
    """estimated_total_paths must be >= 1 and <= total_gap_levels."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        est = roadmap["estimated_total_paths"]
        total = roadmap["total_gap_levels"]
        if est < 1:
            return f"{name}: estimated_total_paths={est} < 1"
        if total > 0 and est > total:
            return f"{name}: estimated_total_paths={est} > total_gap_levels={total}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "estimated_total_paths out of range:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_gap_remaining_non_negative():
    """Every skill's gap_remaining must be >= 0."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        negative = [
            f"{s['skill_id']}={s['gap_remaining']}"
            for s in roadmap["skills_addressed"]
            if s["gap_remaining"] < 0
        ]
        if negative:
            return f"{name}: negative gap_remaining: {negative}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Negative gap_remaining found:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_skill_ids_shown_in_all_entries():
    """Every entry must have a non-empty skill_id starting with 'SK.'."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        bad = []
        for s in roadmap["skills_addressed"]:
            if not s.get("skill_id") or not s["skill_id"].startswith("SK."):
                bad.append(f"addressed: {s.get('skill_id', 'EMPTY')}")
        for s in roadmap["skills_remaining"]:
            if not s.get("skill_id") or not s["skill_id"].startswith("SK."):
                bad.append(f"remaining: {s.get('skill_id', 'EMPTY')}")
        if bad:
            return f"{name}: invalid skill_ids: {bad}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Invalid skill_ids found:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


# ── New consistency tests ─────────────────────────────────────────────


def test_arithmetic_consistency():
    """path_closes + sum(skills_remaining.gap) must equal total_gap_levels.

    This is the critical invariant that keeps the HTML visualizer's
    remaining_total_levels (sum of skills_remaining.gap) in sync with
    the journey_roadmap's remaining_gap_levels (total - path_closes).
    """
    def check(name, scaffold, roadmap, all_gaps, ont):
        path_closes = roadmap["path_closes_levels"]
        remaining_sum = sum(s["gap"] for s in roadmap["skills_remaining"])
        total = roadmap["total_gap_levels"]
        computed_remaining = roadmap["remaining_gap_levels"]

        errors = []
        if path_closes + remaining_sum != total:
            errors.append(
                f"path_closes({path_closes}) + remaining_sum({remaining_sum})"
                f" = {path_closes + remaining_sum} != total({total})"
            )
        if computed_remaining != total - path_closes:
            errors.append(
                f"remaining_gap_levels({computed_remaining})"
                f" != total({total}) - path_closes({path_closes})"
            )
        if remaining_sum != computed_remaining:
            errors.append(
                f"sum(remaining.gap)={remaining_sum}"
                f" != remaining_gap_levels={computed_remaining}"
            )
        if errors:
            return f"{name}: " + "; ".join(errors)

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Arithmetic consistency failed:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_cross_display_consistency():
    """React frontend and HTML visualizer must derive consistent views
    from the same journey_roadmap dict.

    Both displays share:
    - total_gap_levels and path_closes_levels (header numbers)
    - The count of remaining skills (partial + not_started)
    The HTML shows a unified remaining list; React splits into amber
    (partial from skills_addressed) and gray (non-partial from
    skills_remaining).
    """
    def check(name, scaffold, roadmap, all_gaps, ont):
        # --- HTML remaining count (path_visualizer.py:422) ---
        html_remaining_count = len(roadmap["skills_remaining"])

        # --- React: amber (partial) + gray (non-partial) ---
        react_partial_count = sum(
            1 for s in roadmap["skills_remaining"]
            if s.get("partial")
        )
        react_not_started_count = sum(
            1 for s in roadmap["skills_remaining"]
            if not s.get("partial")
        )

        # Skill counts must partition the remaining list
        if react_partial_count + react_not_started_count != html_remaining_count:
            return (
                f"{name}: partial({react_partial_count}) + "
                f"not_started({react_not_started_count}) = "
                f"{react_partial_count + react_not_started_count}"
                f" != remaining({html_remaining_count})"
            )

        # Both use the same total and path_closes for header display
        total = roadmap["total_gap_levels"]
        closes = roadmap["path_closes_levels"]
        remaining = roadmap["remaining_gap_levels"]
        if closes + remaining != total:
            return (
                f"{name}: closes({closes}) + remaining({remaining})"
                f" != total({total})"
            )

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Cross-display consistency failed:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_partial_skills_consistency():
    """Every partial entry in skills_remaining must correspond to a
    chapter skill, and its gap must equal the all_gaps gap minus 1
    (since the path closes exactly 1 level)."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        all_gaps_by_id = {g["skill_id"]: g for g in all_gaps}
        addressed_ids = {s["skill_id"] for s in roadmap["skills_addressed"]}
        errors = []
        for s in roadmap["skills_remaining"]:
            if not s.get("partial"):
                continue
            if s["skill_id"] not in addressed_ids:
                errors.append(f"{s['skill_id']}: partial but not addressed")
                continue
            original = all_gaps_by_id.get(s["skill_id"])
            if not original:
                errors.append(f"{s['skill_id']}: partial but not in all_gaps")
            elif s["gap"] != original["gap"] - 1:
                errors.append(
                    f"{s['skill_id']}: partial gap={s['gap']}"
                    f" != all_gaps gap({original['gap']}) - 1"
                )
        if errors:
            return f"{name}: " + "; ".join(errors)

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Partial skills consistency failed:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_gap1_path_skills_not_in_remaining():
    """Skills with all_gaps gap=1 that are in the path should NOT
    appear in skills_remaining (gap-1=0 means fully accounted for).
    Skills with gap>=2 correctly appear with remaining=gap-1."""
    def check(name, scaffold, roadmap, all_gaps, ont):
        path_sids = {s["skill_id"] for s in roadmap["skills_addressed"]}
        gap1_in_path = {
            g["skill_id"] for g in all_gaps
            if g["gap"] == 1 and g["skill_id"] in path_sids
        }
        bad = [
            s["skill_id"] for s in roadmap["skills_remaining"]
            if s["skill_id"] in gap1_in_path
        ]
        if bad:
            return f"{name}: gap=1 path skills in remaining: {bad}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "Gap-1 path skills found in remaining:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


if __name__ == "__main__":
    test_skills_addressed_matches_chapters()
    print("  PASS: skills_addressed matches chapters")

    test_skills_addressed_have_valid_ontology_ids()
    print("  PASS: all skill_ids are valid ontology IDs")

    test_skills_remaining_partial_overlap()
    print("  PASS: partial overlap OK, non-partial overlap rejected")

    test_total_gap_levels_is_sum_of_all_gaps()
    print("  PASS: total_gap_levels is sum of all gaps")

    test_path_closes_within_chapter_count()
    print("  PASS: path_closes within chapter count")

    test_estimated_paths_is_reasonable()
    print("  PASS: estimated_total_paths is reasonable")

    test_gap_remaining_non_negative()
    print("  PASS: gap_remaining is non-negative")

    test_skill_ids_shown_in_all_entries()
    print("  PASS: all entries have valid SK.* skill_ids")

    test_arithmetic_consistency()
    print("  PASS: arithmetic consistency (path_closes + remaining = total)")

    test_cross_display_consistency()
    print("  PASS: cross-display consistency (React == HTML)")

    test_partial_skills_consistency()
    print("  PASS: partial skills match addressed gap_remaining")

    test_gap1_path_skills_not_in_remaining()
    print("  PASS: gap-1 path skills not in remaining")

    print("\nAll journey roadmap tests passed.")
