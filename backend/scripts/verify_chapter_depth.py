"""Verify chapter depth meets Vivek's reference standard.

Generates a chapter for SK.PRM.003 L2->L3 (matches Vivek's reference example)
and asserts depth requirements from the plan.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.chapter_generator import ChapterGeneratorAgent


def wc(s):
    return len(str(s or "").split())


def verify(spec, skill_id, current_level, target_level):
    """Run all depth assertions. Returns (passed_count, failed_count, failures)."""
    failures = []
    passed = 0

    def check(condition, label):
        nonlocal passed
        if condition:
            passed += 1
            return True
        failures.append(label)
        return False

    # Scenario depth
    scenario = spec.get("scenario", {}) or {}
    check(wc(scenario.get("narrative")) >= 60, f"scenario.narrative >= 60w (got {wc(scenario.get('narrative'))}w)")
    check(scenario.get("a_state", {}).get("quote"), "scenario.a_state.quote populated")
    check(scenario.get("b_state", {}).get("quote"), "scenario.b_state.quote populated")
    check(len(scenario.get("objectives", [])) >= 2, "scenario.objectives >= 2")

    # Concepts depth
    concepts = spec.get("concepts", {}) or {}
    check(bool(concepts.get("mnemonic")), "concepts.mnemonic present")
    check(bool(concepts.get("pull_quote")), "concepts.pull_quote present")
    cards = concepts.get("cards", []) or []
    check(len(cards) >= 2, f"concepts.cards >= 2 (got {len(cards)})")
    for i, c in enumerate(cards):
        for fld in ("identifier", "word", "headline", "body", "analogy"):
            check(bool(c.get(fld)), f"card[{i}].{fld} populated")

    # Example 1 depth
    ex1 = spec.get("example_1", {}) or {}
    check(wc(ex1.get("setup")) >= 30, f"example_1.setup >= 30w (got {wc(ex1.get('setup'))}w)")
    op = ex1.get("original_prompt", {}) or {}
    ip = ex1.get("iterated_prompt", {}) or {}
    check(wc(op.get("output")) >= 30, f"example_1.original_prompt.output >= 30w (got {wc(op.get('output'))}w)")
    check(wc(ip.get("output")) >= 30, f"example_1.iterated_prompt.output >= 30w (got {wc(ip.get('output'))}w)")
    check(bool(op.get("diagnosis")), "example_1.original_prompt.diagnosis populated")
    check(bool(ip.get("diagnosis")), "example_1.iterated_prompt.diagnosis populated")

    steps = ex1.get("steps", []) or []
    check(len(steps) == 3, f"example_1.steps == 3 entries (got {len(steps)})")
    if len(steps) >= 3:
        types = [s.get("content_type") for s in steps[:3]]
        expected = ["diagnosis_checklist", "prompt_variant", "log_entry"]
        check(types == expected, f"example_1.steps content_types {types} == {expected}")
        if steps[0].get("content_type") == "diagnosis_checklist":
            cl = steps[0].get("checklist_items", []) or []
            check(len(cl) >= 3, f"step 1 checklist_items >= 3 (got {len(cl)})")
        if len(steps) >= 3 and steps[2].get("content_type") == "log_entry":
            le = steps[2].get("log_entries", []) or []
            check(len(le) >= 4, f"step 3 log_entries >= 4 (got {len(le)})")

    # Example 2 depth
    ex2 = spec.get("example_2", {}) or {}
    check(wc(ex2.get("setup")) >= 30, f"example_2.setup >= 30w (got {wc(ex2.get('setup'))}w)")
    comparison = ex2.get("comparison", {}) or {}
    variants = comparison.get("variants", []) or []
    check(len(variants) == 2, f"example_2.comparison.variants == 2 (got {len(variants)})")
    for v in variants:
        check(wc(v.get("output")) >= 30, f"variant {v.get('id', '?')}.output >= 30w (got {wc(v.get('output'))}w)")
        check(wc(v.get("why")) >= 20, f"variant {v.get('id', '?')}.why >= 20w (got {wc(v.get('why'))}w)")

    # Agent build depth
    ab = spec.get("agent_build", {}) or {}
    template = ab.get("system_prompt_template", "")
    check(wc(template) >= 100, f"agent_build.system_prompt_template >= 100w (got {wc(template)}w)")
    fields = ab.get("personalization_fields", []) or []
    check(len(fields) >= 3, f"agent_build.personalization_fields >= 3 (got {len(fields)})")
    chips = ab.get("capability_chips", []) or []
    check(len(chips) >= 3, f"agent_build.capability_chips >= 3 (got {len(chips)})")
    # All keys appear in template
    for f in fields:
        key = f.get("key", "")
        if key:
            check(f"{{{key}}}" in template, f"personalization key {{{key}}} appears in template")
    aff = ab.get("final_affirmation", {}) or {}
    check(bool(aff.get("rubric_quote")), "final_affirmation.rubric_quote present")
    check(bool(aff.get("tie_back")), "final_affirmation.tie_back present")

    return passed, len(failures), failures


async def main():
    skill_id = "SK.PRM.003"
    current_level = 2
    target_level = 3

    print(f"Generating chapter: {skill_id} L{current_level}->L{target_level}")
    print("(matches Vivek's reference example)")
    print()

    agent = ChapterGeneratorAgent()
    result = await agent.execute({
        "skill_id": skill_id,
        "current_level": current_level,
        "target_level": target_level,
    })

    spec = result.get("content", {})

    # Save the generated chapter for inspection
    out_path = Path(__file__).parent.parent.parent / "docs" / "depth_verification" / f"{skill_id.replace('.','_')}_L{current_level}_L{target_level}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}")
    print()

    # Run depth checks
    passed, failed, failures = verify(spec, skill_id, current_level, target_level)
    total = passed + failed

    print("=" * 60)
    print(f"DEPTH VERIFICATION: {passed}/{total} checks passed")
    print("=" * 60)
    if failures:
        print()
        print("FAILURES:")
        for f in failures:
            print(f"  - {f}")
    else:
        print()
        print("ALL CHECKS PASSED")

    # Compare against Vivek's reference for sanity
    ref_path = Path(__file__).parent.parent.parent / "docs" / "vivek_apr29" / "example-chapter-spec.json"
    if ref_path.exists():
        ref = json.loads(ref_path.read_text(encoding="utf-8"))
        ref_passed, _, _ = verify(ref, skill_id, current_level, target_level)
        print()
        print(f"For comparison: Vivek's reference passes {ref_passed}/{total}")

    return failed


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main()) == 0 else 1)
