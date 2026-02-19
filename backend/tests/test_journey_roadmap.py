"""Verify journey roadmap computation matches learning path chapters.

The journey roadmap bridges gap analysis (full gaps) and the learning
path (+1 per chapter).  These tests validate:

1. skills_addressed count matches scaffold chapter count
2. All skill_ids are valid ontology IDs (no hallucination)
3. skills_remaining excludes chapter skills
4. total_gap_levels sums correctly from top-10 gaps
5. path_closes_levels equals chapter count
6. estimated_total_paths is reasonable
7. gap_remaining is never negative
8. Every entry has a non-empty skill_id starting with "SK."

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


def compute_roadmap(scaffold_result, state_b, top_10_gaps, ontology):
    """Reproduce the orchestrator's journey_roadmap computation."""
    path_chapters = scaffold_result.get("chapters", [])
    path_skill_ids = {
        ch.get("primary_skill_id") or ch.get("skill_id", "")
        for ch in path_chapters
    }

    total_gap_levels = sum(g["gap"] for g in top_10_gaps if g["gap"] > 0)
    path_closes = len(path_chapters)

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

    skills_remaining = []
    for gap in top_10_gaps:
        if gap["gap"] <= 0 or gap["skill_id"] in path_skill_ids:
            continue
        skills_remaining.append({
            "skill_id": gap["skill_id"],
            "skill_name": gap["skill_name"],
            "domain_label": gap.get("domain_label", ""),
            "current_level": gap["current_level"],
            "required_level": gap["required_level"],
            "gap": gap["gap"],
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


def build_mock_top10_gaps(state_a, state_b, ontology):
    """Build top-10 gap list from state_a/state_b (mimics orchestrator)."""
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
            "rank": 0,
            "skill_id": sid,
            "skill_name": skill["name"],
            "domain": skill["domain"],
            "domain_label": domain["label"] if domain else "",
            "current_level": current,
            "required_level": required,
            "gap": gap,
        })
    gaps.sort(key=lambda g: -g["gap"])
    for i, g in enumerate(gaps[:10], 1):
        g["rank"] = i
    return gaps[:10]


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
        top10 = build_mock_top10_gaps(state_a, state_b, ont)
        roadmap = compute_roadmap(scaffold, state_b, top10, ont)

        result = check_fn(name, scaffold, roadmap, top10, ont)
        if result:
            failures.append(result)

    return failures


def test_skills_addressed_matches_chapters():
    """skills_addressed count must equal scaffold chapter count."""
    def check(name, scaffold, roadmap, top10, ont):
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
    def check(name, scaffold, roadmap, top10, ont):
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


def test_skills_remaining_excludes_chapter_skills():
    """No skill in skills_remaining should also appear in skills_addressed."""
    def check(name, scaffold, roadmap, top10, ont):
        addressed_ids = {s["skill_id"] for s in roadmap["skills_addressed"]}
        overlap = [
            s["skill_id"] for s in roadmap["skills_remaining"]
            if s["skill_id"] in addressed_ids
        ]
        if overlap:
            return f"{name}: overlap: {overlap}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "skills_remaining overlaps with skills_addressed:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_total_gap_levels_is_sum_of_top10():
    """total_gap_levels must equal sum of positive gaps in top-10."""
    def check(name, scaffold, roadmap, top10, ont):
        expected = sum(g["gap"] for g in top10 if g["gap"] > 0)
        actual = roadmap["total_gap_levels"]
        if actual != expected:
            return f"{name}: total={actual}, expected={expected}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "total_gap_levels mismatch:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_path_closes_equals_chapter_count():
    """path_closes_levels must equal the number of chapters."""
    def check(name, scaffold, roadmap, top10, ont):
        n_chapters = len(scaffold["chapters"])
        closes = roadmap["path_closes_levels"]
        if closes != n_chapters:
            return f"{name}: closes={closes}, chapters={n_chapters}"

    failures = _run_for_all_profiles(check)
    assert not failures, (
        "path_closes_levels != chapter count:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )


def test_estimated_paths_is_reasonable():
    """estimated_total_paths must be >= 1 and <= total_gap_levels."""
    def check(name, scaffold, roadmap, top10, ont):
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
    def check(name, scaffold, roadmap, top10, ont):
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
    def check(name, scaffold, roadmap, top10, ont):
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


if __name__ == "__main__":
    test_skills_addressed_matches_chapters()
    print("  PASS: skills_addressed matches chapters")

    test_skills_addressed_have_valid_ontology_ids()
    print("  PASS: all skill_ids are valid ontology IDs")

    test_skills_remaining_excludes_chapter_skills()
    print("  PASS: skills_remaining excludes chapter skills")

    test_total_gap_levels_is_sum_of_top10()
    print("  PASS: total_gap_levels is sum of top-10")

    test_path_closes_equals_chapter_count()
    print("  PASS: path_closes equals chapter count")

    test_estimated_paths_is_reasonable()
    print("  PASS: estimated_total_paths is reasonable")

    test_gap_remaining_non_negative()
    print("  PASS: gap_remaining is non-negative")

    test_skill_ids_shown_in_all_entries()
    print("  PASS: all entries have valid SK.* skill_ids")

    print("\nAll journey roadmap tests passed.")
