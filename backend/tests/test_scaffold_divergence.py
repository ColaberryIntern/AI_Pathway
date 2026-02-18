"""Verify that different profiles produce different deterministic scaffolds.

This test ensures the core personalization guarantee: different
state_a × state_b inputs yield different chapter skill_id selections.
No LLM calls — purely deterministic.
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


def build_inputs(profile: dict, ontology):
    """Build state_a, state_b, and role_context from a profile."""
    state_a = profile["estimated_current_skills"]
    state_b = {}
    for gap_group in profile["expected_skill_gaps"]:
        for sid in gap_group["skills"]:
            skill = ontology.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [g["domain"] for g in profile["expected_skill_gaps"]],
    }
    return state_a, state_b, role_context


def extract_skill_ids(scaffold: dict) -> list[str]:
    """Extract ordered list of primary_skill_id from scaffold chapters."""
    return [ch["primary_skill_id"] for ch in scaffold["chapters"]]


def test_scaffolds_diverge():
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    scaffolds = {}
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        scaffolds[name] = {
            "skill_ids": extract_skill_ids(scaffold),
            "total_chapters": scaffold["total_chapters"],
        }

    # Print comparison table
    print("\n" + "=" * 80)
    print("SCAFFOLD DIVERGENCE TEST")
    print("=" * 80)

    names = [n for _, n in PROFILE_FILES]
    max_chapters = max(s["total_chapters"] for s in scaffolds.values())

    # Header
    header = f"{'Chapter':<10}"
    for name in names:
        header += f"{name:<25}"
    print(header)
    print("-" * 80)

    # Rows
    for i in range(max_chapters):
        row = f"{'Ch ' + str(i + 1):<10}"
        for name in names:
            ids = scaffolds[name]["skill_ids"]
            row += f"{ids[i] if i < len(ids) else '—':<25}"
        print(row)

    # Assert divergence: no two profiles should have identical skill_id sets
    pairs_checked = 0
    pairs_different = 0
    for i, (_, name_a) in enumerate(PROFILE_FILES):
        for j, (_, name_b) in enumerate(PROFILE_FILES):
            if i >= j:
                continue
            ids_a = set(scaffolds[name_a]["skill_ids"])
            ids_b = set(scaffolds[name_b]["skill_ids"])
            pairs_checked += 1
            if ids_a != ids_b:
                pairs_different += 1
            print(
                f"\n{name_a} vs {name_b}: "
                f"{'DIFFERENT' if ids_a != ids_b else 'IDENTICAL'}"
                f" — shared: {ids_a & ids_b or '{none}'}"
                f" — unique to {name_a.split()[0]}: {ids_a - ids_b or '{none}'}"
                f" — unique to {name_b.split()[0]}: {ids_b - ids_a or '{none}'}"
            )

    print(f"\nResult: {pairs_different}/{pairs_checked} pairs produce different scaffolds")

    assert pairs_different == pairs_checked, (
        f"FAIL: Only {pairs_different}/{pairs_checked} profile pairs "
        f"produced different scaffolds. All pairs must differ."
    )
    print("\nPASS: All profile pairs produce different chapter scaffolds.")


if __name__ == "__main__":
    test_scaffolds_diverge()
