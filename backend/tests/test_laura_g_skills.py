"""Anti-hallucination tests for Laura G (profile_13) skill alignment.

Validates that Laura's profile, State A, State B, gap analysis, and
learning path scaffold all conform to the client-approved specification
(Luda's document + Laura's self-assessment feedback).

No LLM calls — purely deterministic.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from app.services.ontology import get_ontology_service
from app.services.gap_engine import SkillGapEngine
from app.services.path_generator import LearningPathGenerator
from app.data.role_templates import ROLE_TEMPLATES

PROFILES_DIR = Path(__file__).parent.parent / "app" / "data" / "profiles"
LAURA_PROFILE_PATH = PROFILES_DIR / "profile_13_laura_g.json"


def load_laura() -> dict:
    with open(LAURA_PROFILE_PATH) as f:
        return json.load(f)


def build_state_b(profile: dict, ontology) -> dict[str, int]:
    """Build state_b mirroring the orchestrator's construction logic.

    - Always adds explicitly-listed skills from expected_skill_gaps
    - If a role template exists: overlay template levels, skip domain expansion
    - If no role template: expand ALL skills from each target domain
    """
    state_b: dict[str, int] = {}
    for gap_group in profile["expected_skill_gaps"]:
        for sid in gap_group["skills"]:
            skill = ontology.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]

    template = ROLE_TEMPLATES.get(profile.get("target_role", ""), {})
    if template:
        # Overlay confirmed target levels; skip full domain expansion
        for sid, level in template.items():
            if sid in state_b:
                state_b[sid] = max(state_b[sid], level)
            else:
                state_b[sid] = level
    else:
        # No template: expand ALL skills from each target domain
        for gap_group in profile["expected_skill_gaps"]:
            domain_id = gap_group.get("domain")
            if domain_id:
                for skill in ontology.get_skills_by_domain(domain_id):
                    sid = skill["id"]
                    if sid not in state_b:
                        state_b[sid] = skill["level"]

    return state_b


# ======================================================================
# Luda-approved expectations
# ======================================================================

# Skills Luda confirmed as CRITICAL for State B (must be in gap analysis)
LUDA_CRITICAL_SKILLS = {
    "SK.AGT.001": 4,   # Tool definitions & validation
    "SK.RAG.000": 4,   # What is RAG and why use it
    "SK.EVL.002": 4,   # LLM-as-judge patterns
    "SK.EVL.001": 4,   # Eval types (offline/online/red team)
    "SK.SEC.001": 3,   # Prompt injection mitigation
}

# Additional HIGH/MODERATE skills from Luda's State B
LUDA_HIGH_SKILLS = {
    "SK.PRM.010": 4,   # JSON/schema outputs
    "SK.PRM.003": 4,   # Prompt debugging & iteration
    "SK.AGT.010": 4,   # Single-agent loops
    "SK.PRD.001": 4,   # Use-case selection & prioritization
    "SK.COM.001": 4,   # Explaining AI to non-technical audiences
}

# All 10 target skills combined
LUDA_ALL_STATE_B = {**LUDA_CRITICAL_SKILLS, **LUDA_HIGH_SKILLS}

# Laura's self-assessed current levels (from Luda's doc)
# Format: skill_id -> (min_level, max_level) where the doc gave ranges
LAURA_STATE_A_EXPECTATIONS = {
    "SK.PRM.001": (0, 1),    # "Martech PMs don't create campaigns"
    "SK.PRM.010": (0, 1),    # "seen it but not using"
    "SK.PRM.003": (1, 2),    # "1-2" range in doc
    "SK.RAG.000": (0, 1),    # "0-1"
    "SK.AGT.000": (0, 1),    # "Zapier = basic awareness"
    "SK.AGT.001": (0, 1),    # "0-1"
    "SK.EVL.001": (0, 1),    # "0-1"
    "SK.EVL.002": (0, 0),    # "0 — no exposure"
    "SK.EVL.020": (0, 0),    # "0 — no exposure"
    "SK.SEC.001": (0, 0),    # "0 — no exposure"
    "SK.COM.001": (1, 2),    # "1-2"
    "SK.PRD.001": (1, 2),    # "1-2"
    "SK.FND.020": (1, 2),    # "1-2"
    "SK.GOV.020": (2, 2),    # "2"
    "SK.PRD.020": (1, 1),    # "1"
}


# ======================================================================
# Tests
# ======================================================================

def test_all_skill_ids_exist_in_ontology():
    """Every skill ID in Laura's profile must exist in the ontology."""
    ont = get_ontology_service()
    profile = load_laura()
    valid_ids = ont.get_all_skill_ids()

    # Check estimated_current_skills
    unknown_current = [
        sid for sid in profile["estimated_current_skills"]
        if sid not in valid_ids
    ]
    assert not unknown_current, (
        f"Unknown skill IDs in estimated_current_skills: {unknown_current}"
    )

    # Check expected_skill_gaps
    unknown_gaps = []
    for gap_group in profile["expected_skill_gaps"]:
        for sid in gap_group["skills"]:
            if sid not in valid_ids:
                unknown_gaps.append(sid)
    assert not unknown_gaps, (
        f"Unknown skill IDs in expected_skill_gaps: {unknown_gaps}"
    )


def test_state_a_matches_self_assessment():
    """Laura's estimated_current_skills must match her documented self-assessment."""
    profile = load_laura()
    current = profile["estimated_current_skills"]

    for sid, (low, high) in LAURA_STATE_A_EXPECTATIONS.items():
        assert sid in current, (
            f"State A missing expected skill {sid}"
        )
        level = current[sid]
        assert low <= level <= high, (
            f"State A {sid}: level {level} outside documented range "
            f"[{low}, {high}]"
        )


def test_state_b_contains_critical_skills():
    """State B (from expected_skill_gaps) must include ALL of Luda's CRITICAL skills."""
    ont = get_ontology_service()
    profile = load_laura()
    state_b = build_state_b(profile, ont)

    missing = [sid for sid in LUDA_CRITICAL_SKILLS if sid not in state_b]
    assert not missing, (
        f"State B missing Luda-confirmed CRITICAL skills: {missing}"
    )


def test_state_b_contains_high_skills():
    """State B must include ALL of Luda's HIGH-priority skills."""
    ont = get_ontology_service()
    profile = load_laura()
    state_b = build_state_b(profile, ont)

    missing = [sid for sid in LUDA_HIGH_SKILLS if sid not in state_b]
    assert not missing, (
        f"State B missing Luda-confirmed HIGH skills: {missing}"
    )


def test_state_b_levels_meet_minimums():
    """State B levels must meet or exceed Luda's documented target levels."""
    ont = get_ontology_service()
    profile = load_laura()
    state_b = build_state_b(profile, ont)

    too_low = []
    for sid, min_level in LUDA_ALL_STATE_B.items():
        actual = state_b.get(sid, 0)
        if actual < min_level:
            too_low.append(f"{sid}: need >={min_level}, got {actual}")

    # Note: state_b is built from ontology tiers which may be lower than
    # Luda's role-specific target. This test validates that the ontology
    # tier is at least as high as the minimum. Skills where the ontology
    # tier is lower should be handled by role templates.
    if too_low:
        print(f"INFO: {len(too_low)} skills below Luda's target "
              f"(expected when ontology tier < role requirement):")
        for msg in too_low:
            print(f"  {msg}")
        # Don't fail — the role template handles the raise.
        # But verify they ARE in the role template.
        template = ROLE_TEMPLATES.get("Martech AI Product Manager", {})
        for sid, min_level in LUDA_ALL_STATE_B.items():
            actual_ont = state_b.get(sid, 0)
            actual_tpl = template.get(sid, actual_ont)
            effective = max(actual_ont, actual_tpl)
            assert effective >= min_level, (
                f"{sid}: even with role template, effective level "
                f"{effective} < Luda minimum {min_level}"
            )


def test_gap_analysis_covers_all_10_skills():
    """Gap analysis must produce gaps for all of Luda's top-10 skills."""
    ont = get_ontology_service()
    engine = SkillGapEngine(ontology_service=ont)
    profile = load_laura()

    state_a = {
        sid: lvl for sid, lvl in profile["estimated_current_skills"].items()
        if ont.get_skill(sid) is not None
    }
    state_b = build_state_b(profile, ont)

    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [
            g["domain"] for g in profile["expected_skill_gaps"]
        ],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }

    gaps = engine.compute_gap(state_a, state_b, role_context=role_context)
    gap_ids = {g["skill_id"] for g in gaps}

    missing = [sid for sid in LUDA_ALL_STATE_B if sid not in gap_ids]
    assert not missing, (
        f"Gap analysis missing Luda's required skills: {missing}. "
        f"Gap IDs found: {sorted(gap_ids)}"
    )


def test_critical_gaps_have_high_delta():
    """Skills marked CRITICAL by Luda must have meaningful gap deltas.

    Target-4 skills (Builder) must have delta >= 2.
    Target-3 skills (Practitioner, e.g. SK.SEC.001) must have delta >= 1
    because the gap engine's skill-level floor raises experienced
    professionals to L2 for ontology-tier-3 skills.
    """
    ont = get_ontology_service()
    engine = SkillGapEngine(ontology_service=ont)
    profile = load_laura()

    state_a = {
        sid: lvl for sid, lvl in profile["estimated_current_skills"].items()
        if ont.get_skill(sid) is not None
    }
    state_b = build_state_b(profile, ont)

    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [
            g["domain"] for g in profile["expected_skill_gaps"]
        ],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }

    gaps = engine.compute_gap(state_a, state_b, role_context=role_context)
    gap_map = {g["skill_id"]: g for g in gaps}

    low_delta = []
    for sid, target_level in LUDA_CRITICAL_SKILLS.items():
        # Target-4 skills need delta >= 2; target-3 need delta >= 1
        min_delta = 2 if target_level >= 4 else 1
        gap = gap_map.get(sid)
        if gap is None:
            low_delta.append(f"{sid}: not in gap list")
        elif gap["delta"] < min_delta:
            low_delta.append(
                f"{sid}: delta={gap['delta']} < {min_delta} "
                f"(current={gap['current_level']}, "
                f"required={gap['required_level']})"
            )

    assert not low_delta, (
        f"CRITICAL skills with insufficient delta: {low_delta}"
    )


def test_scaffold_produces_5_chapters():
    """Learning path scaffold must produce exactly 5 chapters for Laura."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    profile = load_laura()

    state_a = {
        sid: lvl for sid, lvl in profile["estimated_current_skills"].items()
        if ont.get_skill(sid) is not None
    }
    state_b = build_state_b(profile, ont)

    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [
            g["domain"] for g in profile["expected_skill_gaps"]
        ],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }

    scaffold = gen.generate_path(state_a, state_b, role_context=role_context)

    print(f"\nLaura G scaffold: {scaffold['total_chapters']} chapters")
    for ch in scaffold["chapters"]:
        print(f"  Ch{ch['chapter_number']}: {ch['primary_skill_id']} "
              f"({ch['primary_skill_name']}) "
              f"[L{ch['current_level']}->L{ch['target_level']}]")

    assert scaffold["total_chapters"] == 5, (
        f"Expected 5 chapters, got {scaffold['total_chapters']}"
    )


def test_scaffold_no_hallucinated_skills():
    """Every chapter's primary_skill_id must exist in the ontology."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    profile = load_laura()

    state_a = {
        sid: lvl for sid, lvl in profile["estimated_current_skills"].items()
        if ont.get_skill(sid) is not None
    }
    state_b = build_state_b(profile, ont)

    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [
            g["domain"] for g in profile["expected_skill_gaps"]
        ],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }

    scaffold = gen.generate_path(state_a, state_b, role_context=role_context)
    valid_ids = ont.get_all_skill_ids()

    hallucinated = []
    for ch in scaffold["chapters"]:
        sid = ch["primary_skill_id"]
        if sid not in valid_ids:
            hallucinated.append(
                f"Ch{ch['chapter_number']}: {sid}"
            )

    assert not hallucinated, (
        f"Hallucinated skill IDs in scaffold: {hallucinated}"
    )


def test_scaffold_prerequisite_ordering():
    """Prerequisites must appear before dependent skills in chapter order."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    profile = load_laura()

    state_a = {
        sid: lvl for sid, lvl in profile["estimated_current_skills"].items()
        if ont.get_skill(sid) is not None
    }
    state_b = build_state_b(profile, ont)

    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [
            g["domain"] for g in profile["expected_skill_gaps"]
        ],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }

    scaffold = gen.generate_path(state_a, state_b, role_context=role_context)
    chapter_ids = [ch["primary_skill_id"] for ch in scaffold["chapters"]]

    # Build a map of skill -> its position in the path
    position = {sid: idx for idx, sid in enumerate(chapter_ids)}

    violations = []
    for idx, sid in enumerate(chapter_ids):
        skill = ont.get_skill(sid)
        if not skill:
            continue
        for prereq in skill.get("prerequisites", []):
            if prereq in position and position[prereq] > idx:
                violations.append(
                    f"Ch{idx+1} ({sid}) depends on {prereq} "
                    f"which appears later at Ch{position[prereq]+1}"
                )

    assert not violations, (
        f"Prerequisite ordering violations: {violations}"
    )


def test_scaffold_contains_luda_skills():
    """Scaffold must contain at least 4 of Luda's top-10 skills.

    The system produces 5 chapters per path.  One slot may be consumed
    by a prerequisite skill (e.g. SK.PRM.001 as prereq for SK.PRM.010).
    We require at least 4 of 5 chapters to be Luda-confirmed skills.
    """
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    profile = load_laura()

    state_a = {
        sid: lvl for sid, lvl in profile["estimated_current_skills"].items()
        if ont.get_skill(sid) is not None
    }
    state_b = build_state_b(profile, ont)

    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [
            g["domain"] for g in profile["expected_skill_gaps"]
        ],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }

    scaffold = gen.generate_path(state_a, state_b, role_context=role_context)
    chapter_ids = {ch["primary_skill_id"] for ch in scaffold["chapters"]}
    luda_ids = set(LUDA_ALL_STATE_B.keys())

    overlap = chapter_ids & luda_ids
    non_luda = chapter_ids - luda_ids

    print(f"\nScaffold skills: {sorted(chapter_ids)}")
    print(f"Luda overlap:   {sorted(overlap)} ({len(overlap)}/10)")
    if non_luda:
        print(f"Non-Luda slots:  {sorted(non_luda)}")

    assert len(overlap) >= 4, (
        f"Scaffold contains only {len(overlap)}/10 Luda skills "
        f"(need >=4): {sorted(overlap)}. "
        f"Non-Luda chapters: {sorted(non_luda)}"
    )


def test_role_template_matches_luda_spec():
    """The 'Martech AI Product Manager' role template must include all
    Luda-confirmed skills at their documented levels."""
    template = ROLE_TEMPLATES.get("Martech AI Product Manager")
    assert template is not None, (
        "Missing role template for 'Martech AI Product Manager'"
    )

    mismatches = []
    for sid, expected_level in LUDA_ALL_STATE_B.items():
        actual = template.get(sid)
        if actual is None:
            mismatches.append(f"{sid}: missing from template")
        elif actual < expected_level:
            mismatches.append(
                f"{sid}: template={actual}, Luda minimum={expected_level}"
            )

    assert not mismatches, (
        f"Role template mismatches with Luda spec: {mismatches}"
    )


if __name__ == "__main__":
    tests = [
        test_all_skill_ids_exist_in_ontology,
        test_state_a_matches_self_assessment,
        test_state_b_contains_critical_skills,
        test_state_b_contains_high_skills,
        test_state_b_levels_meet_minimums,
        test_gap_analysis_covers_all_10_skills,
        test_critical_gaps_have_high_delta,
        test_scaffold_produces_5_chapters,
        test_scaffold_no_hallucinated_skills,
        test_scaffold_prerequisite_ordering,
        test_scaffold_contains_luda_skills,
        test_role_template_matches_luda_spec,
    ]
    for test in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test.__name__}")
        print("=" * 60)
        test()
        print(f"PASS: {test.__name__}")

    print(f"\n\nAll {len(tests)} Laura G anti-hallucination tests passed.")
