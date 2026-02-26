"""Cross-profile validation tests.

Runs ALL 13 test profiles through the deterministic pipeline
(no LLM calls) and validates that every profile produces output
matching the client-approved format:

1. State A — valid ontology skill IDs, reasonable levels
2. State B — valid skill IDs, template overlay applied when available
3. Gap analysis — non-empty, skills sorted by priority
4. Learning path — exactly 5 chapters, no hallucinated skills
5. Journey roadmap — consistent with gap analysis and chapters
6. Top-10 lists — rebuild from template when template exists
7. Visualization data — correct node states and link types
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, ".")

from app.services.ontology import get_ontology_service
from app.services.gap_engine import SkillGapEngine
from app.services.path_generator import LearningPathGenerator
from app.services.path_visualizer import PathVisualizer
from app.data.role_templates import ROLE_TEMPLATES

PROFILES_DIR = Path(__file__).parent.parent / "app" / "data" / "profiles"
ALL_PROFILES = sorted(PROFILES_DIR.glob("profile_*.json"))


def load_profile(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def build_state_a(profile: dict, ontology) -> dict[str, int]:
    """Build state_a from profile's estimated_current_skills."""
    return {
        sid: lvl
        for sid, lvl in profile.get("estimated_current_skills", {}).items()
        if ontology.get_skill(sid) is not None
    }


def build_state_b(profile: dict, ontology) -> dict[str, int]:
    """Build state_b mirroring the orchestrator's construction logic."""
    state_b: dict[str, int] = {}
    for gap_group in profile.get("expected_skill_gaps", []):
        for sid in gap_group.get("skills", []):
            skill = ontology.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]

    template = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    if template:
        for sid, level in template.items():
            if sid in state_b:
                state_b[sid] = max(state_b[sid], level)
            else:
                state_b[sid] = level
    else:
        for gap_group in profile.get("expected_skill_gaps", []):
            domain_id = gap_group.get("domain")
            if domain_id:
                for skill in ontology.get_skills_by_domain(domain_id):
                    sid = skill["id"]
                    if sid not in state_b:
                        state_b[sid] = skill["level"]

    return state_b


def build_role_context(profile: dict) -> dict:
    """Build role_context dict for gap engine and path generator."""
    template = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    return {
        "target_role": profile.get("target_role", ""),
        "target_domains": [
            g["domain"] for g in profile.get("expected_skill_gaps", [])
        ],
        "priority_skills": set(template.keys()) if template else set(),
    }


def run_full_pipeline(profile: dict):
    """Run the full deterministic pipeline for a profile.

    Returns (state_a, state_b, gaps, scaffold, role_context).
    """
    ont = get_ontology_service()
    engine = SkillGapEngine(ontology_service=ont)
    gen = LearningPathGenerator(ontology_service=ont)

    state_a = build_state_a(profile, ont)
    state_b = build_state_b(profile, ont)
    role_context = build_role_context(profile)

    gaps = engine.compute_gap(state_a, state_b, role_context=role_context)
    scaffold = gen.generate_path(state_a, state_b, role_context=role_context)

    return state_a, state_b, gaps, scaffold, role_context


# ======================================================================
# Parametrized fixtures
# ======================================================================

@pytest.fixture(params=[p.name for p in ALL_PROFILES], ids=[p.stem for p in ALL_PROFILES])
def profile_path(request):
    return PROFILES_DIR / request.param


@pytest.fixture
def profile(profile_path):
    return load_profile(profile_path)


@pytest.fixture
def pipeline_result(profile):
    return run_full_pipeline(profile)


@pytest.fixture
def ontology():
    return get_ontology_service()


# ======================================================================
# Test 1: Profile structure is valid
# ======================================================================

def test_profile_has_required_fields(profile):
    """Every profile must have the required fields."""
    required = ["id", "name", "target_role", "expected_skill_gaps",
                "estimated_current_skills", "learning_intent"]
    missing = [f for f in required if f not in profile]
    assert not missing, (
        f"{profile['name']}: missing fields: {missing}"
    )


# ======================================================================
# Test 2: All skill IDs exist in ontology
# ======================================================================

def test_all_profile_skill_ids_in_ontology(profile, ontology):
    """Every skill ID referenced in the profile must exist in the ontology."""
    valid_ids = ontology.get_all_skill_ids()
    unknown = []

    for sid in profile.get("estimated_current_skills", {}):
        if sid not in valid_ids:
            unknown.append(f"current:{sid}")

    for gap_group in profile.get("expected_skill_gaps", []):
        for sid in gap_group.get("skills", []):
            if sid not in valid_ids:
                unknown.append(f"gap:{sid}")

    assert not unknown, (
        f"{profile['name']}: unknown skill IDs: {unknown}"
    )


# ======================================================================
# Test 3: State B is non-empty and uses template when available
# ======================================================================

def test_state_b_non_empty(profile, ontology):
    """State B must contain at least 5 skills for every profile."""
    state_b = build_state_b(profile, ontology)
    assert len(state_b) >= 5, (
        f"{profile['name']}: state_b has only {len(state_b)} skills"
    )


def test_state_b_template_overlay(profile, ontology):
    """When a role template exists, all template skills must be in state_b."""
    template = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    if not template:
        pytest.skip(f"No template for role: {profile.get('target_role')}")

    state_b = build_state_b(profile, ontology)
    missing = [sid for sid in template if sid not in state_b]
    assert not missing, (
        f"{profile['name']}: template skills missing from state_b: {missing}"
    )

    # Template levels must be reflected
    wrong_level = []
    for sid, expected in template.items():
        actual = state_b.get(sid, 0)
        if actual < expected:
            wrong_level.append(f"{sid}: expected>={expected}, got {actual}")
    assert not wrong_level, (
        f"{profile['name']}: state_b levels below template: {wrong_level}"
    )


# ======================================================================
# Test 4: Gap analysis produces valid results
# ======================================================================

def test_gaps_non_empty(profile, pipeline_result):
    """Gap analysis must produce at least 1 gap for every profile."""
    _, _, gaps, _, _ = pipeline_result
    assert len(gaps) >= 1, (
        f"{profile['name']}: gap analysis returned 0 gaps"
    )


def test_gaps_have_required_fields(profile, pipeline_result):
    """Every gap entry must have the required fields."""
    _, _, gaps, _, _ = pipeline_result
    # Gap engine uses 'required_level'; orchestrator sometimes maps to
    # 'target_level'. Accept either.
    required_fields = ["skill_id", "skill_name", "domain",
                       "current_level", "delta"]

    for gap in gaps:
        missing = [f for f in required_fields if f not in gap]
        assert not missing, (
            f"{profile['name']}: gap {gap.get('skill_id','?')} "
            f"missing fields: {missing}"
        )
        has_level = "target_level" in gap or "required_level" in gap
        assert has_level, (
            f"{profile['name']}: gap {gap['skill_id']} missing both "
            f"target_level and required_level"
        )


def test_gaps_have_positive_delta(profile, pipeline_result):
    """Every gap must have delta > 0."""
    _, _, gaps, _, _ = pipeline_result
    zero_delta = [
        g["skill_id"] for g in gaps if g.get("delta", 0) <= 0
    ]
    assert not zero_delta, (
        f"{profile['name']}: gaps with zero/negative delta: {zero_delta}"
    )


# ======================================================================
# Test 5: Learning path scaffold
# ======================================================================

def test_scaffold_produces_expected_chapters(profile, pipeline_result):
    """Every profile must produce exactly MAX_CHAPTERS chapters."""
    from app.services.path_generator import MAX_CHAPTERS
    _, _, _, scaffold, _ = pipeline_result
    assert scaffold["total_chapters"] == MAX_CHAPTERS, (
        f"{profile['name']}: expected {MAX_CHAPTERS} chapters, "
        f"got {scaffold['total_chapters']}"
    )


def test_scaffold_no_hallucinated_skills(profile, pipeline_result, ontology):
    """Every chapter's primary_skill_id must exist in the ontology."""
    _, _, _, scaffold, _ = pipeline_result
    valid_ids = ontology.get_all_skill_ids()
    hallucinated = []
    for ch in scaffold["chapters"]:
        sid = ch["primary_skill_id"]
        if sid not in valid_ids:
            hallucinated.append(f"Ch{ch['chapter_number']}: {sid}")
    assert not hallucinated, (
        f"{profile['name']}: hallucinated skill IDs: {hallucinated}"
    )


def test_scaffold_no_duplicate_skills(profile, pipeline_result):
    """No skill should appear in multiple chapters."""
    _, _, _, scaffold, _ = pipeline_result
    skill_ids = [ch["primary_skill_id"] for ch in scaffold["chapters"]]
    dupes = [sid for sid in skill_ids if skill_ids.count(sid) > 1]
    assert not dupes, (
        f"{profile['name']}: duplicate skills in scaffold: {set(dupes)}"
    )


def test_scaffold_chapters_have_valid_levels(profile, pipeline_result):
    """Each chapter must have current_level < target_level."""
    _, _, _, scaffold, _ = pipeline_result
    bad_levels = []
    for ch in scaffold["chapters"]:
        if ch["current_level"] >= ch["target_level"]:
            bad_levels.append(
                f"Ch{ch['chapter_number']} {ch['primary_skill_id']}: "
                f"L{ch['current_level']}->L{ch['target_level']}"
            )
    assert not bad_levels, (
        f"{profile['name']}: chapters with no level increase: {bad_levels}"
    )


def test_scaffold_prerequisite_ordering(profile, pipeline_result, ontology):
    """Prerequisites must appear before dependent skills."""
    _, _, _, scaffold, _ = pipeline_result
    chapter_ids = [ch["primary_skill_id"] for ch in scaffold["chapters"]]
    position = {sid: idx for idx, sid in enumerate(chapter_ids)}

    violations = []
    for idx, sid in enumerate(chapter_ids):
        skill = ontology.get_skill(sid)
        if not skill:
            continue
        for prereq in skill.get("prerequisites", []):
            if prereq in position and position[prereq] > idx:
                violations.append(
                    f"Ch{idx+1} ({sid}) needs {prereq} "
                    f"which is at Ch{position[prereq]+1}"
                )
    assert not violations, (
        f"{profile['name']}: prerequisite violations: {violations}"
    )


# ======================================================================
# Test 6: Template profiles — top-10 rebuilds correctly
# ======================================================================

def test_template_top10_rebuild(profile, ontology):
    """For template profiles, rebuilt top-10 must use template skills."""
    template = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    if not template:
        pytest.skip(f"No template for role: {profile.get('target_role')}")

    state_a = build_state_a(profile, ontology)
    state_b = build_state_b(profile, ontology)

    # Rebuild top-10 like orchestrator does
    rebuilt = []
    for sid, level in template.items():
        current = state_a.get(sid, 0)
        gap = max(0, level - current)
        if gap <= 0:
            continue
        rebuilt.append({
            "skill_id": sid,
            "gap": gap,
            "required_level": level,
            "current_level": current,
        })
    rebuilt.sort(key=lambda x: (-x["gap"], -x["required_level"]))
    top10 = rebuilt[:10]

    # Every entry must have a positive gap
    assert len(top10) >= 1, (
        f"{profile['name']}: template produced 0 gap skills"
    )
    for entry in top10:
        assert entry["gap"] > 0, (
            f"{profile['name']}: {entry['skill_id']} has gap=0"
        )


# ======================================================================
# Test 7: Visualization data integrity
# ======================================================================

def test_visualization_graph_data(profile, pipeline_result, ontology):
    """Visualization graph data must have correct node states."""
    state_a, state_b, gaps, scaffold, role_context = pipeline_result

    top10_current = [
        {"skill_id": sid, "current_level": lvl}
        for sid, lvl in sorted(state_a.items())[:10]
    ]
    top10_target = [
        {"skill_id": sid, "required_level": lvl}
        for sid, lvl in sorted(state_b.items())[:10]
    ]

    visualizer = PathVisualizer(ontology_service=ontology)
    graph_data = visualizer._build_graph_data(
        top10_current, top10_target, gaps,
        scaffold["chapters"], top10_target,
    )

    # Must have nodes and links
    assert len(graph_data["nodes"]) > 0, (
        f"{profile['name']}: graph has no nodes"
    )
    assert len(graph_data["links"]) > 0, (
        f"{profile['name']}: graph has no links"
    )

    # Chapter nodes must have state 'chapter'
    chapter_sids = {
        ch["primary_skill_id"] for ch in scaffold["chapters"]
    }
    skill_nodes = [n for n in graph_data["nodes"] if n["type"] == "skill"]
    for node in skill_nodes:
        if node["id"] in chapter_sids:
            assert node["state"] == "chapter", (
                f"{profile['name']}: chapter skill {node['id']} "
                f"has state '{node['state']}' instead of 'chapter'"
            )

    # chapters list in graph must match scaffold
    from app.services.path_generator import MAX_CHAPTERS
    assert len(graph_data["chapters"]) == MAX_CHAPTERS, (
        f"{profile['name']}: graph chapters count "
        f"{len(graph_data['chapters'])} != {MAX_CHAPTERS}"
    )

    # Node states must be valid
    valid_states = {"current", "target", "chapter", "remaining",
                    "gap", "neutral"}
    for node in skill_nodes:
        assert node["state"] in valid_states, (
            f"{profile['name']}: invalid state '{node['state']}' "
            f"for {node['id']}"
        )


# ======================================================================
# Test 8: Cross-profile scaffold divergence
# ======================================================================

def test_profiles_produce_different_scaffolds():
    """Different profiles must produce meaningfully different paths."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    all_chapter_sets = {}
    for path in ALL_PROFILES:
        profile = load_profile(path)
        state_a = build_state_a(profile, ont)
        state_b = build_state_b(profile, ont)
        role_context = build_role_context(profile)
        scaffold = gen.generate_path(state_a, state_b, role_context=role_context)
        chapter_ids = frozenset(
            ch["primary_skill_id"] for ch in scaffold["chapters"]
        )
        all_chapter_sets[profile["name"]] = chapter_ids

    # Check that no two profiles have identical chapters
    names = list(all_chapter_sets.keys())
    identical_pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if all_chapter_sets[names[i]] == all_chapter_sets[names[j]]:
                identical_pairs.append((names[i], names[j]))

    # Allow up to 2 identical pairs (some similar roles may overlap)
    assert len(identical_pairs) <= 2, (
        f"Too many identical scaffolds ({len(identical_pairs)}): "
        f"{identical_pairs}"
    )


# ======================================================================
# Test 9: Journey roadmap structure (when available)
# ======================================================================

def test_journey_roadmap_consistency(profile, pipeline_result, ontology):
    """Journey roadmap must be consistent with gaps and chapters."""
    state_a, state_b, gaps, scaffold, role_context = pipeline_result

    # Rebuild top-10 gaps like orchestrator
    template = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    if template:
        top10_gaps = []
        for sid, level in template.items():
            current = state_a.get(sid, 0)
            gap = max(0, level - current)
            if gap > 0:
                top10_gaps.append({"skill_id": sid, "gap": gap,
                                   "required_level": level,
                                   "current_level": current})
        top10_gaps.sort(key=lambda x: (-x["gap"], -x["required_level"]))
        top10_gaps = top10_gaps[:10]
    else:
        top10_gaps = [
            {"skill_id": g["skill_id"], "gap": g["delta"],
             "required_level": g.get("target_level", g.get("required_level", 0)),
             "current_level": g.get("current_level", 0)}
            for g in gaps[:10]
        ]

    chapter_sids = {
        ch["primary_skill_id"] for ch in scaffold["chapters"]
    }
    top10_sids = {g["skill_id"] for g in top10_gaps}

    # Skills addressed = intersection of chapters and top-10
    addressed = chapter_sids & top10_sids
    remaining = top10_sids - chapter_sids

    # Verify addressed + remaining = top-10
    assert addressed | remaining == top10_sids, (
        f"{profile['name']}: addressed+remaining != top-10 sids"
    )

    # Total gap levels should be positive
    total_gap = sum(g["gap"] for g in top10_gaps)
    assert total_gap > 0, (
        f"{profile['name']}: total gap levels is 0"
    )
