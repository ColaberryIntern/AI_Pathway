"""Verify that gap analysis matches learning path chapters after reconciliation.

The orchestrator reconciles the LLM gap analyzer output with the
deterministic scaffold so that the frontend displays consistent data.
This test validates that:

1. Gap skill_ids exactly match scaffold chapter primary_skill_ids
2. Gap count equals chapter count
3. Gap levels (current/target) match chapter levels
4. Summary totals are consistent with the gap list
5. The reconciliation uses correct field names from the scaffold

No LLM calls — tests the reconciliation logic in isolation.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from app.services.path_generator import LearningPathGenerator
from app.services.ontology import get_ontology_service
from app.data.role_templates import ROLE_TEMPLATES

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
    ("profile_13_laura_g.json", "Laura G"),
    ("profile_14_jenny_boavista.json", "Jenny Boavista"),
]


def load_profile(filename: str) -> dict:
    with open(PROFILES_DIR / filename) as f:
        return json.load(f)


def build_inputs(profile: dict, ontology):
    """Build state_a, state_b, and role_context from a profile.

    Mirrors the orchestrator's state_b construction:
    - Always adds explicitly-listed skills from expected_skill_gaps
    - If a role template exists: overlay template levels, skip domain expansion
    - If no role template: expand ALL skills from each target domain
    """
    state_a = profile["estimated_current_skills"]
    state_b = {}
    for gap_group in profile["expected_skill_gaps"]:
        for sid in gap_group["skills"]:
            skill = ontology.get_skill(sid)
            if skill:
                state_b[sid] = skill["level"]

    template = ROLE_TEMPLATES.get(profile.get("target_role", ""))
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

    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [g["domain"] for g in profile["expected_skill_gaps"]],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }
    return state_a, state_b, role_context


def reconcile_gaps(scaffold_result: dict, ontology) -> dict:
    """Reproduce the orchestrator's gap reconciliation logic.

    This mirrors the code in orchestrator.py (lines 205-236) so we can
    test it independently without LLM calls.
    """
    scaffold_chapters = scaffold_result.get("chapters", [])
    if not scaffold_chapters:
        return {"gaps": [], "summary": {}}

    aligned_gaps = []
    for ch in scaffold_chapters:
        sid = ch.get("primary_skill_id", ch.get("skill_id", ""))
        skill = ontology.get_skill(sid)
        domain = skill["domain"] if skill else ""
        skill_name = ch.get("primary_skill_name", ch.get("skill_name", sid))
        current = ch.get("current_level", 0)
        target = ch.get("target_level", 1)
        aligned_gaps.append({
            "skill_id": sid,
            "skill_name": skill_name,
            "domain": domain,
            "current_level": current,
            "target_level": target,
            "gap": target - current,
            "priority": ch.get("chapter_number", 0),
            "priority_reason": "Selected by deterministic gap engine",
        })

    summary = {
        "total_gaps": len(aligned_gaps),
        "critical_gaps": len([g for g in aligned_gaps if g["gap"] >= 2]),
        "primary_domains": list({
            g["domain"] for g in aligned_gaps if g.get("domain")
        }),
    }

    return {"gaps": aligned_gaps, "summary": summary}


def test_gap_chapter_skill_ids_match():
    """Gap skill_ids must exactly match scaffold chapter primary_skill_ids."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    print("\n" + "=" * 80)
    print("GAP-CHAPTER CONSISTENCY TEST")
    print("=" * 80)

    failures = []
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        reconciled = reconcile_gaps(scaffold, ont)

        chapter_skill_ids = [
            ch["primary_skill_id"] for ch in scaffold["chapters"]
        ]
        gap_skill_ids = [g["skill_id"] for g in reconciled["gaps"]]

        print(f"\n--- {name} ---")
        print(f"  Scaffold chapters: {chapter_skill_ids}")
        print(f"  Reconciled gaps:   {gap_skill_ids}")

        if set(chapter_skill_ids) != set(gap_skill_ids):
            failures.append(
                f"{name}: chapters={chapter_skill_ids}, gaps={gap_skill_ids}"
            )
            print("  FAIL: Skill IDs do not match!")
        else:
            print("  OK: Skill IDs match.")

    assert not failures, (
        f"FAIL: Gap-chapter skill_id mismatch in:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print("\nPASS: All profiles have matching gap and chapter skill IDs.")


def test_gap_count_matches_chapter_count():
    """Number of reconciled gaps must equal number of scaffold chapters."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    print("\n" + "=" * 80)
    print("GAP COUNT = CHAPTER COUNT TEST")
    print("=" * 80)

    failures = []
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        reconciled = reconcile_gaps(scaffold, ont)

        n_chapters = len(scaffold["chapters"])
        n_gaps = len(reconciled["gaps"])
        summary_total = reconciled["summary"]["total_gaps"]

        status = "OK" if n_gaps == n_chapters == summary_total else "FAIL"
        print(f"  {name}: chapters={n_chapters}, gaps={n_gaps}, summary={summary_total} [{status}]")

        if n_gaps != n_chapters:
            failures.append(f"{name}: {n_gaps} gaps != {n_chapters} chapters")
        if summary_total != n_gaps:
            failures.append(f"{name}: summary.total_gaps={summary_total} != {n_gaps} gaps")

    assert not failures, (
        f"FAIL: Count mismatches:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print("\nPASS: Gap count matches chapter count for all profiles.")


def test_gap_levels_match_chapter_levels():
    """Reconciled gap current/target levels must match scaffold chapter levels."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    print("\n" + "=" * 80)
    print("GAP LEVELS = CHAPTER LEVELS TEST")
    print("=" * 80)

    failures = []
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        reconciled = reconcile_gaps(scaffold, ont)

        chapter_levels = {
            ch["primary_skill_id"]: (ch["current_level"], ch["target_level"])
            for ch in scaffold["chapters"]
        }
        gap_levels = {
            g["skill_id"]: (g["current_level"], g["target_level"])
            for g in reconciled["gaps"]
        }

        print(f"\n--- {name} ---")
        mismatched = []
        for sid, (gc, gt) in gap_levels.items():
            cc, ct = chapter_levels.get(sid, (None, None))
            if (gc, gt) != (cc, ct):
                mismatched.append(f"    {sid}: gap=L{gc}->L{gt}, chapter=L{cc}->L{ct}")
                print(f"  MISMATCH: {sid}: gap=L{gc}->L{gt}, chapter=L{cc}->L{ct}")
            else:
                print(f"  OK: {sid}: L{gc}->L{gt}")

        if mismatched:
            failures.append(f"{name}:\n" + "\n".join(mismatched))

    assert not failures, (
        f"FAIL: Level mismatches:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print("\nPASS: Gap levels match chapter levels for all profiles.")


def test_reconciled_gaps_have_valid_fields():
    """Every reconciled gap must have non-empty skill_id, skill_name, and domain."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    print("\n" + "=" * 80)
    print("RECONCILED GAP FIELD VALIDITY TEST")
    print("=" * 80)

    failures = []
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        reconciled = reconcile_gaps(scaffold, ont)

        print(f"\n--- {name} ---")
        for i, gap in enumerate(reconciled["gaps"]):
            issues = []
            if not gap.get("skill_id"):
                issues.append("empty skill_id")
            if not gap.get("skill_name"):
                issues.append("empty skill_name")
            if not gap.get("domain"):
                issues.append("empty domain")
            if gap.get("gap", 0) <= 0:
                issues.append(f"non-positive gap={gap.get('gap')}")

            if issues:
                msg = f"  Gap {i+1} ({gap.get('skill_id', '???')}): {', '.join(issues)}"
                print(f"  FAIL: {msg}")
                failures.append(f"{name} gap {i+1}: {', '.join(issues)}")
            else:
                print(f"  OK: {gap['skill_id']} ({gap['skill_name']}, {gap['domain']})")

    assert not failures, (
        f"FAIL: Invalid gap fields:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print("\nPASS: All reconciled gaps have valid fields.")


def test_summary_domains_match_gap_domains():
    """summary.primary_domains must match the unique domains in the gap list."""
    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)

    print("\n" + "=" * 80)
    print("SUMMARY DOMAINS CONSISTENCY TEST")
    print("=" * 80)

    failures = []
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)
        reconciled = reconcile_gaps(scaffold, ont)

        gap_domains = {g["domain"] for g in reconciled["gaps"] if g.get("domain")}
        summary_domains = set(reconciled["summary"].get("primary_domains", []))

        status = "OK" if gap_domains == summary_domains else "FAIL"
        print(f"  {name}: gap_domains={sorted(gap_domains)}, summary={sorted(summary_domains)} [{status}]")

        if gap_domains != summary_domains:
            failures.append(f"{name}: {gap_domains} != {summary_domains}")

    assert not failures, (
        f"FAIL: Domain mismatches:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print("\nPASS: Summary domains match gap domains for all profiles.")


def test_mandatory_category_coverage():
    """Every profile's scaffold must cover all 4 mandatory categories.

    Categories:
    - Foundation: D.FND
    - Applied AI:  D.PRM, D.RAG, D.AGT, D.MOD, D.MUL, D.OPS, D.TOOL
    - Evaluation:  D.EVL
    - Safety:      D.SEC, D.GOV

    Exception: when a role template exists and indicates a category is
    awareness-only (all template skills in that category are L <= 1)
    and the learner already meets those levels, the category can
    legitimately be absent from the scaffold.
    """
    from app.services.path_generator import MANDATORY_CATEGORIES
    from app.services.gap_engine import SkillGapEngine
    from app.services.state_inference import expand_state_a

    ont = get_ontology_service()
    gen = LearningPathGenerator(ontology_service=ont)
    engine = SkillGapEngine(ontology_service=ont)

    print("\n" + "=" * 80)
    print("MANDATORY CATEGORY COVERAGE TEST")
    print("=" * 80)

    failures = []
    for filename, name in PROFILE_FILES:
        profile = load_profile(filename)
        state_a, state_b, rc = build_inputs(profile, ont)
        scaffold = gen.generate_path(state_a, state_b, role_context=rc)

        # Compute actual gaps to determine which categories are active
        expanded_a = expand_state_a(state_a, ont)[0]
        gaps = engine.compute_gap(expanded_a, state_b, role_context=rc)
        gap_domains = {g["domain"] for g in gaps}

        chapter_domains = set()
        for ch in scaffold["chapters"]:
            skill = ont.get_skill(ch["primary_skill_id"])
            if skill:
                chapter_domains.add(skill["domain"])

        has_template = bool(rc.get("priority_skills"))

        missing = []
        for cat in MANDATORY_CATEGORIES:
            cat_domains = set(cat["domains"])
            if not chapter_domains & cat_domains:
                # Allow missing if template-aware and no gaps in category
                if has_template and not (cat_domains & gap_domains):
                    continue  # awareness-only, learner meets it
                missing.append(cat["name"])

        status = "OK" if not missing else "FAIL"
        print(f"  {name}: domains={sorted(chapter_domains)}, missing={missing} [{status}]")
        if missing:
            failures.append(f"{name}: missing {missing}")

    assert not failures, (
        f"FAIL: Missing mandatory categories:\n"
        + "\n".join(f"  - {f}" for f in failures)
    )
    print("\nPASS: All profiles cover all 4 mandatory categories.")


if __name__ == "__main__":
    test_gap_chapter_skill_ids_match()
    test_gap_count_matches_chapter_count()
    test_gap_levels_match_chapter_levels()
    test_reconciled_gaps_have_valid_fields()
    test_summary_domains_match_gap_domains()
    test_mandatory_category_coverage()
    print("\n" + "=" * 80)
    print("ALL GAP-CHAPTER CONSISTENCY TESTS PASSED")
    print("=" * 80)
