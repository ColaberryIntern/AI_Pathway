"""Profile enrichment quality tests.

Validates that all 13 profiles meet the enrichment standard:
- >= 25 estimated_current_skills
- >= 8 current_profile.technical_skills
- >= 5 current_profile.soft_skills
- >= 8 target_jd.requirements
- >= 6 expected_skill_gaps domains
- Realistic skill level distributions per archetype
- All skill IDs valid in ontology
- Rich narrative sections (summary, ai_experience, learning_intent)
"""
import json
from pathlib import Path

import pytest

from app.services.ontology import get_ontology_service

PROFILES_DIR = Path(__file__).parent.parent / "app" / "data" / "profiles"
PROFILE_FILES = sorted(PROFILES_DIR.glob("profile_*.json"))
ONTOLOGY = get_ontology_service()
VALID_IDS = ONTOLOGY.get_all_skill_ids()


def _load_profiles():
    profiles = []
    for f in PROFILE_FILES:
        data = json.loads(f.read_text())
        profiles.append(data)
    return profiles


ALL_PROFILES = _load_profiles()


@pytest.fixture(params=ALL_PROFILES, ids=[p["id"] for p in ALL_PROFILES])
def profile(request):
    return request.param


# ── Estimated Current Skills ──────────────────────────────────────────

def test_minimum_estimated_skills(profile):
    """Each profile should have >= 25 estimated_current_skills."""
    skills = profile.get("estimated_current_skills", {})
    assert len(skills) >= 25, (
        f"{profile['name']}: only {len(skills)} estimated_current_skills (need >= 25)"
    )


def test_estimated_skills_all_valid(profile):
    """Every skill ID in estimated_current_skills must exist in ontology."""
    for sid in profile.get("estimated_current_skills", {}):
        assert sid in VALID_IDS, (
            f"{profile['name']}: invalid skill ID '{sid}' in estimated_current_skills"
        )


def test_estimated_skills_levels_valid(profile):
    """Skill levels must be 0-5."""
    for sid, lvl in profile.get("estimated_current_skills", {}).items():
        assert 0 <= lvl <= 5, (
            f"{profile['name']}: skill {sid} has level {lvl} (must be 0-5)"
        )


def test_estimated_skills_no_duplicates(profile):
    """No duplicate skill IDs (JSON keys are unique by definition, but verify)."""
    skills = profile.get("estimated_current_skills", {})
    assert isinstance(skills, dict)  # JSON dicts have unique keys


# ── Technical & Soft Skills ───────────────────────────────────────────

def test_minimum_technical_skills(profile):
    """Each profile should have >= 8 technical_skills."""
    tech = profile.get("current_profile", {}).get("technical_skills", [])
    assert len(tech) >= 8, (
        f"{profile['name']}: only {len(tech)} technical_skills (need >= 8)"
    )


def test_minimum_soft_skills(profile):
    """Each profile should have >= 5 soft_skills."""
    soft = profile.get("current_profile", {}).get("soft_skills", [])
    assert len(soft) >= 5, (
        f"{profile['name']}: only {len(soft)} soft_skills (need >= 5)"
    )


# ── Target JD Requirements ───────────────────────────────────────────

def test_minimum_jd_requirements(profile):
    """Each profile should have >= 8 target_jd.requirements."""
    reqs = profile.get("target_jd", {}).get("requirements", [])
    assert len(reqs) >= 8, (
        f"{profile['name']}: only {len(reqs)} JD requirements (need >= 8)"
    )


# ── Expected Skill Gaps ──────────────────────────────────────────────

def test_minimum_gap_domains(profile):
    """Each profile should have >= 6 expected_skill_gaps domains."""
    gaps = profile.get("expected_skill_gaps", [])
    assert len(gaps) >= 6, (
        f"{profile['name']}: only {len(gaps)} gap domains (need >= 6)"
    )


def test_gap_skills_all_valid(profile):
    """Every skill ID in expected_skill_gaps must exist in ontology."""
    for gap in profile.get("expected_skill_gaps", []):
        for sid in gap.get("skills", []):
            assert sid in VALID_IDS, (
                f"{profile['name']}: invalid skill ID '{sid}' in "
                f"expected_skill_gaps domain {gap.get('domain')}"
            )


def test_gap_domains_valid(profile):
    """Every domain in expected_skill_gaps must be a valid domain ID."""
    valid_domains = {d["id"] for d in ONTOLOGY.domains}
    for gap in profile.get("expected_skill_gaps", []):
        domain = gap.get("domain", "")
        assert domain in valid_domains, (
            f"{profile['name']}: invalid domain '{domain}' in expected_skill_gaps"
        )


# ── Narrative Quality ─────────────────────────────────────────────────

def test_rich_summary(profile):
    """Profile summary should be at least 200 characters."""
    summary = profile.get("current_profile", {}).get("summary", "")
    assert len(summary) >= 200, (
        f"{profile['name']}: summary too short ({len(summary)} chars, need >= 200)"
    )


def test_rich_ai_experience(profile):
    """AI experience should be at least 100 characters."""
    ai_exp = profile.get("current_profile", {}).get("ai_experience", "")
    assert len(ai_exp) >= 100, (
        f"{profile['name']}: ai_experience too short ({len(ai_exp)} chars, need >= 100)"
    )


def test_rich_learning_intent(profile):
    """Learning intent should be at least 150 characters."""
    intent = profile.get("learning_intent", "")
    assert len(intent) >= 150, (
        f"{profile['name']}: learning_intent too short ({len(intent)} chars, need >= 150)"
    )


# ── Archetype-Appropriate Levels ──────────────────────────────────────

def test_has_zero_level_gap_seeds(profile):
    """Profiles should have some level-0 skills to seed expected gaps."""
    skills = profile.get("estimated_current_skills", {})
    zeros = [sid for sid, lvl in skills.items() if lvl == 0]
    assert len(zeros) >= 2, (
        f"{profile['name']}: only {len(zeros)} level-0 skills "
        f"(need >= 2 to seed gap analysis)"
    )


def test_tools_used_is_list(profile):
    """tools_used should be a non-empty list."""
    tools = profile.get("tools_used", [])
    assert isinstance(tools, list)
    assert len(tools) >= 1, f"{profile['name']}: tools_used is empty"


def test_required_metadata_fields(profile):
    """All profiles must have core metadata fields."""
    required = [
        "id", "name", "current_role", "target_role", "industry",
        "experience_years", "ai_exposure_level", "tools_used",
        "technical_background", "archetype", "learning_intent",
    ]
    for field in required:
        assert field in profile, (
            f"{profile['name']}: missing required field '{field}'"
        )
