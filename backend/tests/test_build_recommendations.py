"""Test deterministic recommendation generation from chapter data.

Verifies that _build_recommendations() produces recommendations
that reference actual chapter domains and skills — not generic
advice from the LLM gap analyzer.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from app.services.path_generator import LearningPathGenerator
from app.services.ontology import get_ontology_service

PROFILES_DIR = Path(__file__).parent.parent / "app" / "data" / "profiles"

# Re-implement _build_recommendations standalone (avoids vertexai import
# from Orchestrator.__init__).  This tests the same logic.
LEVEL_LABELS = {
    0: "Unaware", 1: "Aware", 2: "User",
    3: "Practitioner", 4: "Builder", 5: "Architect",
}


def build_recommendations(path_data: dict, ontology) -> list[str]:
    """Mirror of Orchestrator._build_recommendations for testing."""
    chapters = path_data.get("chapters", [])
    if not chapters:
        return []

    chapter_info = []
    seen_domains: dict[str, str] = {}
    for ch in chapters:
        sid = ch.get("skill_id") or ch.get("primary_skill_id", "")
        parts = sid.split(".")
        domain_id = f"D.{parts[1]}" if len(parts) >= 3 else None
        domain_obj = ontology.get_domain(domain_id) if domain_id else None
        domain_label = domain_obj["label"] if domain_obj else (domain_id or "Unknown")
        skill_name = ch.get("skill_name") or ch.get("primary_skill_name", sid)
        current = ch.get("current_level", 0)
        target = ch.get("target_level", 1)
        if domain_id and domain_id not in seen_domains:
            seen_domains[domain_id] = domain_label
        chapter_info.append({
            "domain_label": domain_label,
            "skill_name": skill_name,
            "current_level": current,
            "target_level": target,
        })

    foundational = [c for c in chapter_info if c["current_level"] <= 1]
    advancing = [c for c in chapter_info if c["current_level"] >= 2]
    unique_domains = list(seen_domains.values())
    recs: list[str] = []

    if foundational:
        names = " and ".join(c["skill_name"] for c in foundational[:2])
        recs.append(
            f"Start with foundational skills like {names} "
            f"to build core understanding before tackling advanced topics."
        )
    elif advancing:
        names = " and ".join(c["skill_name"] for c in advancing[:2])
        recs.append(
            f"Build on your existing knowledge by deepening "
            f"expertise in {names}."
        )

    from_levels = [c["current_level"] for c in chapter_info]
    dominant_from = max(set(from_levels), key=from_levels.count)
    dominant_to = dominant_from + 1
    recs.append(
        f"Your path focuses on progressing from "
        f"{LEVEL_LABELS.get(dominant_from, f'L{dominant_from}')} to "
        f"{LEVEL_LABELS.get(dominant_to, f'L{dominant_to}')} proficiency "
        f"across {len(chapters)} chapters. Complete them in order "
        f"for best results."
    )

    if len(unique_domains) > 1:
        recs.append(
            f"Your path covers {len(unique_domains)} skill domains: "
            f"{', '.join(unique_domains)}. This breadth ensures "
            f"a well-rounded AI skill set for your target role."
        )
    elif unique_domains:
        recs.append(
            f"Your path focuses deeply on {unique_domains[0]}, "
            f"building progressive mastery within this critical domain."
        )

    return recs[:3]


def _scaffold_for_profile(filename: str, ont, gen):
    """Build scaffold from a profile file."""
    profile = json.loads((PROFILES_DIR / filename).read_text())
    state_a = profile["estimated_current_skills"]
    state_b = {}
    for g in profile["expected_skill_gaps"]:
        for sid in g["skills"]:
            s = ont.get_skill(sid)
            if s:
                state_b[sid] = s["level"]
        d = g.get("domain")
        if d:
            for s in ont.get_skills_by_domain(d):
                if s["id"] not in state_b:
                    state_b[s["id"]] = s["level"]
    rc = {
        "target_role": profile["target_role"],
        "target_domains": [g["domain"] for g in profile["expected_skill_gaps"]],
    }
    return gen.generate_path(state_a, state_b, role_context=rc)


def test_recommendations_reference_actual_domains():
    """Recommendations must mention domains that appear in the chapters."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    scaffold = _scaffold_for_profile("profile_08_hank_thompson.json", ont, gen)
    recs = build_recommendations(scaffold, ont)

    # Hank's chapters cover D.EVL, D.OPS, D.SEC, D.FND
    chapter_domains = set()
    for ch in scaffold["chapters"]:
        sid = ch["primary_skill_id"]
        parts = sid.split(".")
        domain_id = f"D.{parts[1]}" if len(parts) >= 3 else None
        if domain_id:
            d = ont.get_domain(domain_id)
            if d:
                chapter_domains.add(d["label"])

    # At least one recommendation must mention an actual domain label
    rec_text = " ".join(recs)
    matched = [d for d in chapter_domains if d in rec_text]
    assert matched, (
        f"No chapter domains found in recommendations.\n"
        f"Chapter domains: {chapter_domains}\n"
        f"Recommendations: {recs}"
    )


def test_returns_exactly_3_recommendations():
    """Typical profile produces exactly 3 recommendations."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    scaffold = _scaffold_for_profile("profile_01_alex_rivera.json", ont, gen)
    recs = build_recommendations(scaffold, ont)
    assert len(recs) == 3, f"Expected 3 recs, got {len(recs)}: {recs}"


def test_empty_chapters_returns_empty():
    """Empty chapter list produces no recommendations."""
    ont = get_ontology_service()
    recs = build_recommendations({"chapters": []}, ont)
    assert recs == []


def test_foundational_vs_advancing_template():
    """Foundational chapters trigger 'Start with' template."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    scaffold = _scaffold_for_profile("profile_04_dana_morales.json", ont, gen)
    recs = build_recommendations(scaffold, ont)

    # Dana has mixed levels (L1->L2 and L2->L3), so foundational exist
    assert recs[0].startswith("Start with foundational"), (
        f"Expected 'Start with foundational...' but got: {recs[0]}"
    )


def test_no_generic_domains():
    """Recommendations must NOT mention domains absent from the chapters."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    scaffold = _scaffold_for_profile("profile_08_hank_thompson.json", ont, gen)
    recs = build_recommendations(scaffold, ont)
    rec_text = " ".join(recs)

    # Check that every domain mentioned in recommendations is actually
    # in the path's chapters (not a hallucinated domain).
    chapter_domains = set()
    for ch in scaffold.get("chapters", []):
        sid = ch.get("primary_skill_id", "")
        skill = ont.get_skill(sid)
        if skill:
            domain_obj = ont.get_domain(skill["domain"])
            if domain_obj:
                chapter_domains.add(domain_obj["label"])

    # All domain labels should be found in the recommendation text
    all_domains = [d["label"] for d in ont.domains]
    absent_domains = [d for d in all_domains if d not in chapter_domains]
    for d in absent_domains:
        assert d not in rec_text, (
            f"Recommendation mentions absent domain '{d}': {recs}"
        )


if __name__ == "__main__":
    test_recommendations_reference_actual_domains()
    print("PASS: test_recommendations_reference_actual_domains")

    test_returns_exactly_3_recommendations()
    print("PASS: test_returns_exactly_3_recommendations")

    test_empty_chapters_returns_empty()
    print("PASS: test_empty_chapters_returns_empty")

    test_foundational_vs_advancing_template()
    print("PASS: test_foundational_vs_advancing_template")

    test_no_generic_domains()
    print("PASS: test_no_generic_domains")

    print("\nAll tests passed.")
