"""Verify state_b fallback when JD parser returns invalid skill IDs.

Simulates the scenario where RAG is unavailable and the JD parser
returns invented IDs like "SKL001".  The orchestrator should fall back
to building state_b from the profile's expected_skill_gaps.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from app.services.path_generator import LearningPathGenerator
from app.services.ontology import get_ontology_service

PROFILES_DIR = Path(__file__).parent.parent / "app" / "data" / "profiles"

PROFILE_FILES = [
    ("profile_01_alex_rivera.json", "Alex Rivera"),
    ("profile_02_bethany_chen.json", "Bethany Chen"),
    ("profile_03_charles_patel.json", "Charles Patel"),
]


def load_profile(filename: str) -> dict:
    with open(PROFILES_DIR / filename) as f:
        return json.load(f)


def test_fallback_produces_chapters():
    """When valid_state_b is empty, fallback to expected_skill_gaps produces chapters."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)

        # Simulate: LLM returned all-invalid state_b (like SKL001)
        fake_llm_state_b = {"SKL001": 3, "SKL002": 4, "SKL003": 2}
        valid_state_b = {
            sid: lvl for sid, lvl in fake_llm_state_b.items()
            if ont.get_skill(sid) is not None
        }
        assert valid_state_b == {}, "Fake IDs should all be filtered out"

        # Apply fallback: build state_b from expected_skill_gaps
        if not valid_state_b and "expected_skill_gaps" in profile:
            for gap_group in profile["expected_skill_gaps"]:
                for sid in gap_group.get("skills", []):
                    skill = ont.get_skill(sid)
                    if skill:
                        valid_state_b[sid] = skill["level"]

        assert len(valid_state_b) > 0, (
            f"Fallback state_b should have skills for {name}, "
            f"got {len(valid_state_b)}"
        )

        # Build state_a from profile
        state_a = profile.get("estimated_current_skills", {})
        valid_state_a = {
            sid: lvl for sid, lvl in state_a.items()
            if ont.get_skill(sid) is not None
        }

        # Build role_context
        role_context = {
            "target_role": profile.get("target_role", ""),
            "target_domains": [
                g["domain"]
                for g in profile.get("expected_skill_gaps", [])
                if "domain" in g
            ],
        }

        scaffold = gen.generate_path(valid_state_a, valid_state_b, role_context=role_context)

        print(f"\n{name}: {scaffold['total_chapters']} chapters")
        for ch in scaffold["chapters"]:
            print(f"  Ch {ch['chapter_number']}: {ch['primary_skill_id']} "
                  f"({ch['primary_skill_name']}) [{ch['current_level']}->{ch['target_level']}]")

        assert scaffold["total_chapters"] > 0, (
            f"{name} should produce >0 chapters with fallback state_b, "
            f"got {scaffold['total_chapters']}"
        )


def test_fallback_diverges_across_profiles():
    """Different profiles with fallback state_b still produce different scaffolds."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    scaffolds = {}
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)

        state_a = {
            sid: lvl for sid, lvl in profile.get("estimated_current_skills", {}).items()
            if ont.get_skill(sid) is not None
        }

        # Build state_b from expected_skill_gaps (the fallback path)
        state_b = {}
        for gap_group in profile.get("expected_skill_gaps", []):
            for sid in gap_group.get("skills", []):
                skill = ont.get_skill(sid)
                if skill:
                    state_b[sid] = skill["level"]

        role_context = {
            "target_role": profile.get("target_role", ""),
            "target_domains": [
                g["domain"]
                for g in profile.get("expected_skill_gaps", [])
                if "domain" in g
            ],
        }

        scaffold = gen.generate_path(state_a, state_b, role_context=role_context)
        scaffolds[name] = [ch["primary_skill_id"] for ch in scaffold["chapters"]]

    # All pairs must differ
    names = [n for _, n in PROFILE_FILES]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ids_a = set(scaffolds[names[i]])
            ids_b = set(scaffolds[names[j]])
            print(f"\n{names[i]} vs {names[j]}: "
                  f"{'DIFFERENT' if ids_a != ids_b else 'IDENTICAL'}")
            assert ids_a != ids_b, (
                f"{names[i]} and {names[j]} produced identical scaffolds "
                f"with fallback state_b: {ids_a}"
            )


if __name__ == "__main__":
    test_fallback_produces_chapters()
    print("\n" + "=" * 60)
    test_fallback_diverges_across_profiles()
    print("\n\nAll fallback tests passed.")
