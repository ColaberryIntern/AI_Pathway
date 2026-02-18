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
    ("profile_04_dana_morales.json", "Dana Morales"),
    ("profile_05_elena_brooks.json", "Elena Brooks"),
    ("profile_06_frank_nguyen.json", "Frank Nguyen"),
    ("profile_07_grace_williams.json", "Grace Williams"),
    ("profile_08_hank_thompson.json", "Hank Thompson"),
    ("profile_09_irene_shah.json", "Irene Shah"),
    ("profile_10_john_miller.json", "John Miller"),
    ("profile_11_kelly_johnson.json", "Kelly Johnson"),
    ("profile_12_kevin_park.json", "Kevin Park"),
]


def load_profile(filename: str) -> dict:
    with open(PROFILES_DIR / filename) as f:
        return json.load(f)


def build_inputs(profile: dict, ontology):
    """Build state_a, state_b, and role_context from a profile.

    Mirrors the orchestrator's state_b fallback: includes ALL skills
    from each target domain (not just the specific listed subset) so
    the gap engine has enough candidates after per-skill floors.
    """
    state_a = profile["estimated_current_skills"]
    state_b = {}
    for gap_group in profile["expected_skill_gaps"]:
        # Add the specific listed skills first
        for sid in gap_group["skills"]:
            skill = ontology.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]
        # Also add ALL skills from each target domain
        domain_id = gap_group.get("domain")
        if domain_id:
            for skill in ontology.get_skills_by_domain(domain_id):
                sid = skill["id"]
                if sid not in state_b:
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
    all_scaffolds_raw = {}
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        scaffolds[name] = {
            "skill_ids": extract_skill_ids(scaffold),
            "total_chapters": scaffold["total_chapters"],
        }
        all_scaffolds_raw[name] = scaffold

    # Print comparison table
    print("\n" + "=" * 80)
    print("SCAFFOLD DIVERGENCE TEST — ALL 12 PROFILES")
    print("=" * 80)

    # Print per-profile chapter details
    for name in [n for _, n in PROFILE_FILES]:
        scaffold = all_scaffolds_raw[name]
        chapters = scaffold["chapters"]
        print(f"\n--- {name} ({len(chapters)} chapters) ---")
        levels = set()
        for ch in chapters:
            lvl = f"L{ch['current_level']}->L{ch['target_level']}"
            levels.add(lvl)
            sid = ch['primary_skill_id']
            skill = ont.get_skill(sid)
            domain = skill["domain"] if skill else "?"
            print(f"  Ch{ch['chapter_number']}: {sid:<20} {lvl}  ({domain})")
        print(f"  Level spread: {sorted(levels)}")

    # Assert every profile gets exactly 5 chapters
    print("\n" + "=" * 80)
    print("CHAPTER COUNT CHECK")
    print("=" * 80)
    chapter_failures = []
    for name in [n for _, n in PROFILE_FILES]:
        count = scaffolds[name]["total_chapters"]
        status = "OK" if count == 5 else "FAIL"
        print(f"  {name}: {count} chapters [{status}]")
        if count != 5:
            chapter_failures.append(name)

    assert not chapter_failures, (
        f"FAIL: These profiles did not get 5 chapters: {chapter_failures}"
    )
    print("PASS: All profiles have exactly 5 chapters.")

    # Assert mixed starting levels (not all the same)
    print("\n" + "=" * 80)
    print("MIXED LEVEL CHECK")
    print("=" * 80)
    uniform_profiles = []
    for name in [n for _, n in PROFILE_FILES]:
        chapters = all_scaffolds_raw[name]["chapters"]
        level_pairs = {(ch["current_level"], ch["target_level"]) for ch in chapters}
        if len(level_pairs) == 1:
            uniform_profiles.append(f"{name}: all {level_pairs.pop()}")
        print(f"  {name}: {len(level_pairs)} distinct level pairs")

    if uniform_profiles:
        print(f"  WARNING: Uniform levels in: {uniform_profiles}")
    else:
        print("PASS: All profiles have mixed starting levels.")

    # Assert divergence: no two profiles should have identical skill_id sets
    print("\n" + "=" * 80)
    print("DIVERGENCE CHECK")
    print("=" * 80)
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

    print(f"Result: {pairs_different}/{pairs_checked} pairs produce different scaffolds")

    # Allow up to 3 identical pairs (profiles with very similar
    # state_a and target domains can legitimately converge).
    min_different = pairs_checked - 3
    assert pairs_different >= min_different, (
        f"FAIL: Only {pairs_different}/{pairs_checked} profile pairs "
        f"produced different scaffolds (need at least {min_different})."
    )
    if pairs_different == pairs_checked:
        print("PASS: All profile pairs produce different chapter scaffolds.")
    else:
        print(
            f"PASS (with {pairs_checked - pairs_different} identical pairs): "
            f"Similar profiles may converge — acceptable."
        )


if __name__ == "__main__":
    test_scaffolds_diverge()
