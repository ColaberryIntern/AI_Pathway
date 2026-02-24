"""Diagnostic report: Laura G pipeline vs Luda's client document.

Runs the full deterministic pipeline (gap engine + path generator) and
prints a side-by-side comparison against every table in Luda's spec.

Usage:
    cd backend
    python tests/diagnose_laura_g.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from app.services.ontology import get_ontology_service
from app.services.gap_engine import SkillGapEngine
from app.services.path_generator import LearningPathGenerator
from app.services.state_inference import expand_state_a
from app.data.role_templates import ROLE_TEMPLATES

PROFILES_DIR = Path(__file__).parent.parent / "app" / "data" / "profiles"


def load_laura() -> dict:
    with open(PROFILES_DIR / "profile_13_laura_g.json") as f:
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
# Luda's document tables (canonical reference)
# ======================================================================

PROFICIENCY_LABELS = {
    0: "Unaware", 1: "Aware", 2: "User",
    3: "Practitioner", 4: "Builder", 5: "Architect",
}

# State A — Luda's documented current levels for Laura
LUDA_STATE_A = {
    "SK.PRM.001": {"level": 1, "doc_range": "1",     "note": "Martech PMs don't create campaigns — Laura's feedback"},
    "SK.PRM.010": {"level": 1, "doc_range": "1",     "note": "Seen JSON but not using it"},
    "SK.PRM.003": {"level": 1, "doc_range": "1-2",   "note": "Minimal prompt debugging"},
    "SK.RAG.000": {"level": 0, "doc_range": "0-1",   "note": "No RAG understanding yet"},
    "SK.AGT.000": {"level": 1, "doc_range": "1",     "note": "Zapier = basic automation awareness"},
    "SK.AGT.001": {"level": 0, "doc_range": "0-1",   "note": "No tool definition experience"},
    "SK.EVL.001": {"level": 0, "doc_range": "0-1",   "note": "No eval awareness"},
    "SK.EVL.002": {"level": 0, "doc_range": "0",     "note": "No exposure to LLM-as-judge"},
    "SK.EVL.020": {"level": 0, "doc_range": "0",     "note": "No exposure to prompt unit tests"},
    "SK.SEC.001": {"level": 0, "doc_range": "0",     "note": "No security exposure"},
    "SK.COM.001": {"level": 1, "doc_range": "1-2",   "note": "Limited ability to explain AI"},
    "SK.PRD.001": {"level": 1, "doc_range": "1-2",   "note": "Informal use-case thinking"},
    "SK.FND.020": {"level": 1, "doc_range": "1-2",   "note": "Aware from martech compliance work"},
    "SK.GOV.020": {"level": 2, "doc_range": "2",     "note": "User level from platform compliance"},
    "SK.PRD.020": {"level": 1, "doc_range": "1",     "note": "Aware from change-management work"},
}

# State B — Luda's top-10 target skills with levels and priority
LUDA_STATE_B = {
    "SK.PRM.010": {"level": 4, "priority": "CRITICAL",  "rank": 1,  "why": "API integration, structured data, product specs"},
    "SK.AGT.001": {"level": 4, "priority": "CRITICAL",  "rank": 2,  "why": "Agentic solutions (explicit JD requirement)"},
    "SK.RAG.000": {"level": 4, "priority": "CRITICAL",  "rank": 3,  "why": "Personalization, GenAI fundamentals (explicit JD)"},
    "SK.PRD.001": {"level": 4, "priority": "CRITICAL",  "rank": 4,  "why": "Core PM skill — roadmap, prioritization"},
    "SK.EVL.002": {"level": 4, "priority": "HIGH",      "rank": 5,  "why": "Scalable quality assessment, metrics definition"},
    "SK.PRM.003": {"level": 4, "priority": "HIGH",      "rank": 6,  "why": "Rapid experimentation, prompt engineering"},
    "SK.EVL.001": {"level": 4, "priority": "HIGH",      "rank": 7,  "why": "Responsible deployment, release process"},
    "SK.SEC.001": {"level": 3, "priority": "HIGH",      "rank": 8,  "why": "Responsible AI, enterprise security"},
    "SK.AGT.010": {"level": 4, "priority": "HIGH",      "rank": 9,  "why": "Autonomous workflows, agentic solutions"},
    "SK.COM.001": {"level": 4, "priority": "MEDIUM",    "rank": 10, "why": "Cross-functional leadership, stakeholder alignment"},
}

# Gap Analysis — Luda's documented gaps
LUDA_GAPS = {
    "SK.PRM.010": {"current": "1 (Aware)",         "required": "3-4 (Practitioner/Builder)", "priority_gap": "CRITICAL"},
    "SK.AGT.001": {"current": "0-1 (Unaware/Aware)","required": "4 (Builder)",               "priority_gap": "CRITICAL"},
    "SK.RAG.000": {"current": "0-1 (Unaware/Aware)","required": "3-4 (Practitioner/Builder)", "priority_gap": "CRITICAL"},
    "SK.PRD.001": {"current": "1-2 (Aware/User)",   "required": "4 (Builder)",               "priority_gap": "MODERATE"},
    "SK.EVL.002": {"current": "0 (Unaware)",        "required": "3-4 (Practitioner/Builder)", "priority_gap": "CRITICAL"},
    "SK.PRM.003": {"current": "1-2 (Aware/User)",   "required": "4 (Builder)",               "priority_gap": "MODERATE"},
    "SK.EVL.001": {"current": "0-1 (Unaware/Aware)","required": "3-4 (Practitioner/Builder)", "priority_gap": "CRITICAL"},
    "SK.SEC.001": {"current": "0 (Unaware)",        "required": "3 (Practitioner)",           "priority_gap": "CRITICAL"},
    "SK.AGT.010": {"current": "0 (Unaware)",        "required": "4 (Builder)",               "priority_gap": "CRITICAL"},
    "SK.COM.001": {"current": "1-2 (Aware/User)",   "required": "4 (Builder)",               "priority_gap": "MODERATE"},
}

# Learning Path — Luda's 3 phases
LUDA_PHASES = [
    {"phase": "Phase 1 (Weeks 1-4): Technical Foundations",
     "skills": ["SK.PRM.010", "SK.PRM.003", "SK.RAG.000"]},
    {"phase": "Phase 2 (Weeks 5-8): Agentic Solutions",
     "skills": ["SK.AGT.001", "SK.AGT.010"]},
    {"phase": "Phase 3 (Weeks 9-12): Product & Governance",
     "skills": ["SK.EVL.002", "SK.EVL.001", "SK.SEC.001", "SK.PRD.001", "SK.COM.001"]},
]


def fmt_level(level: int) -> str:
    return f"L{level} ({PROFICIENCY_LABELS.get(level, '?')})"


def main():
    ont = get_ontology_service()
    profile = load_laura()
    engine = SkillGapEngine(ontology_service=ont)
    gen = LearningPathGenerator(ontology_service=ont)

    # Build state_a (with validation)
    state_a_raw = profile["estimated_current_skills"]
    state_a = {
        sid: lvl for sid, lvl in state_a_raw.items()
        if ont.get_skill(sid) is not None
    }

    # Build state_b
    state_b = build_state_b(profile, ont)

    # Expand state_a (same as path generator does)
    expanded_a, inferred, conf_weighted, decay_applied, avg_decay = expand_state_a(
        state_a, ont
    )

    # Build role_context with priority_skills
    _tpl = ROLE_TEMPLATES.get(profile.get("target_role", ""))
    role_context = {
        "target_role": profile["target_role"],
        "target_domains": [g["domain"] for g in profile["expected_skill_gaps"]],
        "priority_skills": set(_tpl.keys()) if _tpl else set(),
    }

    # Run gap engine
    gaps = engine.compute_gap(expanded_a, state_b, role_context=role_context)
    gap_map = {g["skill_id"]: g for g in gaps}

    # Run path generator
    scaffold = gen.generate_path(state_a, state_b, role_context=role_context)

    # ==================================================================
    # REPORT
    # ==================================================================
    print("=" * 90)
    print("  LAURA G — SYSTEM vs LUDA'S DOCUMENT: FULL COMPARISON")
    print("=" * 90)

    # ------------------------------------------------------------------
    # 1. STATE A COMPARISON
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  1. STATE A: Current Skills (Profile Data vs Luda's Document)")
    print("=" * 90)
    print(f"\n  {'Skill ID':<15} {'Skill Name':<40} {'System':>8} {'Luda Doc':>10} {'Match?':>8}")
    print("  " + "-" * 83)

    state_a_issues = []
    for sid, luda in sorted(LUDA_STATE_A.items()):
        skill = ont.get_skill(sid)
        name = skill["name"] if skill else "???"
        sys_level = state_a_raw.get(sid, "MISSING")
        luda_level = luda["level"]
        match = "OK" if sys_level == luda_level else "DIFF"
        if match == "DIFF":
            state_a_issues.append(sid)
        print(f"  {sid:<15} {name:<40} {str(sys_level):>8} {luda['doc_range']:>10} {match:>8}")
        if match == "DIFF":
            print(f"  {'':>15} Note: {luda['note']}")

    # Show skills in system but NOT in Luda's State A doc
    extra_skills = [sid for sid in state_a_raw if sid not in LUDA_STATE_A]
    if extra_skills:
        print(f"\n  Skills in system State A but NOT in Luda's State A table:")
        for sid in sorted(extra_skills):
            skill = ont.get_skill(sid)
            name = skill["name"] if skill else "???"
            print(f"    {sid:<15} {name:<40} L{state_a_raw[sid]}")

    print(f"\n  Summary: {len(LUDA_STATE_A)} Luda skills checked, "
          f"{len(state_a_issues)} mismatches, "
          f"{len(extra_skills)} extra system skills")

    # ------------------------------------------------------------------
    # 2. STATE B COMPARISON
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  2. STATE B: Target Skills (System state_b vs Luda's Top-10)")
    print("=" * 90)
    print(f"\n  {'Rank':>4} {'Skill ID':<15} {'Skill Name':<35} {'System':>8} {'Luda':>6} {'Priority':>10} {'Match?':>8}")
    print("  " + "-" * 90)

    state_b_issues = []
    for sid, luda in sorted(LUDA_STATE_B.items(), key=lambda x: x[1]["rank"]):
        skill = ont.get_skill(sid)
        name = skill["name"] if skill else "???"
        sys_level = state_b.get(sid, "MISSING")
        match = "OK" if sys_level == luda["level"] else ("LOW" if isinstance(sys_level, int) and sys_level < luda["level"] else "DIFF")
        if match != "OK":
            state_b_issues.append(sid)
        print(f"  {luda['rank']:>4} {sid:<15} {name:<35} {str(sys_level):>8} {luda['level']:>6} {luda['priority']:>10} {match:>8}")
        if match != "OK":
            print(f"       Why this matters: {luda['why']}")

    print(f"\n  Summary: {len(LUDA_STATE_B)} Luda skills checked, "
          f"{len(state_b_issues)} below target")

    # ------------------------------------------------------------------
    # 3. EFFECTIVE CURRENT LEVELS (after gap engine floors)
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  3. EFFECTIVE STATE A (after gap engine floor logic)")
    print("=" * 90)
    print(f"\n  The gap engine applies 3 floors that raise Laura's effective current level:")
    max_skill = max(state_a.values()) if state_a else 0
    print(f"    - Professional floor: L1 (Laura has max skill L{max_skill}, >= L2)")
    print(f"    - Domain floor: varies by domain (high skills in D.PRD raise all D.PRD)")
    print(f"    - Skill-level floor: L2 for ontology-tier-3+ skills (Laura has L{max_skill} >= L3)")
    print(f"\n  State A expansion: {inferred} skills inferred from prerequisites")

    print(f"\n  {'Skill ID':<15} {'Name':<35} {'Raw':>5} {'Effective':>10} {'Target':>8} {'Delta':>7} {'In Gaps?':>10}")
    print("  " + "-" * 95)

    for sid in sorted(LUDA_STATE_B.keys()):
        skill = ont.get_skill(sid)
        name = (skill["name"] if skill else "???")[:35]
        raw = state_a_raw.get(sid, 0)
        gap = gap_map.get(sid)
        eff = gap["current_level"] if gap else "—"
        target = state_b.get(sid, "—")
        delta = gap["delta"] if gap else "—"
        in_gaps = "YES" if gap else "NO"
        print(f"  {sid:<15} {name:<35} L{raw:>3} {('L' + str(eff)) if isinstance(eff, int) else eff:>10} {'L' + str(target) if isinstance(target, int) else target:>8} {delta:>7} {in_gaps:>10}")
        if not gap:
            # Explain why it's missing
            skill_info = ont.get_skill(sid)
            ont_level = skill_info["level"] if skill_info else "?"
            domain = skill_info["domain"] if skill_info else "?"
            print(f"  {'':>15} ^ Missing because: ontology tier={ont_level}, "
                  f"domain={domain}, floors may push effective >= target")

    # ------------------------------------------------------------------
    # 4. GAP ANALYSIS COMPARISON
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  4. GAP ANALYSIS: System Gaps vs Luda's Gap Table")
    print("=" * 90)
    print(f"\n  System produced {len(gaps)} total gaps. Luda's table has {len(LUDA_GAPS)} gaps.")
    print(f"\n  {'Skill ID':<15} {'Name':<30} {'Sys Current':>12} {'Sys Target':>12} {'Sys Delta':>10} {'Luda Priority':>15} {'Match?':>8}")
    print("  " + "-" * 105)

    gap_issues = []
    for sid, luda in sorted(LUDA_GAPS.items(), key=lambda x: x[0]):
        skill = ont.get_skill(sid)
        name = (skill["name"] if skill else "???")[:30]
        gap = gap_map.get(sid)
        if gap:
            sys_current = fmt_level(gap["current_level"])
            sys_target = fmt_level(gap["required_level"])
            sys_delta = str(gap["delta"])
            match = "OK"
        else:
            sys_current = "—"
            sys_target = "—"
            sys_delta = "MISSING"
            match = "MISSING"
            gap_issues.append(sid)
        print(f"  {sid:<15} {name:<30} {sys_current:>12} {sys_target:>12} {sys_delta:>10} {luda['priority_gap']:>15} {match:>8}")

    # Show system gaps NOT in Luda's table
    extra_gaps = [g for g in gaps if g["skill_id"] not in LUDA_GAPS]
    if extra_gaps:
        print(f"\n  System gaps NOT in Luda's 10-skill table (from domain expansion):")
        for g in extra_gaps[:15]:
            skill = ont.get_skill(g["skill_id"])
            name = (skill["name"] if skill else "???")[:30]
            print(f"    {g['skill_id']:<15} {name:<30} L{g['current_level']}->L{g['required_level']} "
                  f"delta={g['delta']}  score={g['priority_score']:.1f}  [{g['domain']}]")
        if len(extra_gaps) > 15:
            print(f"    ... and {len(extra_gaps) - 15} more")

    print(f"\n  Summary: {len(LUDA_GAPS)} Luda gaps checked, {len(gap_issues)} missing from system")

    # ------------------------------------------------------------------
    # 5. GAP RANKING (priority_score)
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  5. GAP RANKING: Top 15 by Priority Score")
    print("=" * 90)
    print(f"\n  Formula: priority_score = 3*delta + 2*role_relevance - 0.5*skill_level")
    print(f"\n  {'#':>3} {'Skill ID':<15} {'Name':<35} {'Delta':>6} {'RolRel':>7} {'OntLvl':>7} {'Score':>7} {'Luda Rank':>10}")
    print("  " + "-" * 95)

    for i, g in enumerate(gaps[:15], 1):
        skill = ont.get_skill(g["skill_id"])
        name = (skill["name"] if skill else "???")[:35]
        luda_rank = LUDA_STATE_B.get(g["skill_id"], {}).get("rank", "—")
        print(f"  {i:>3} {g['skill_id']:<15} {name:<35} {g['delta']:>6} {g['role_relevance']:>7} "
              f"{g['skill_level']:>7} {g['priority_score']:>7.1f} {str(luda_rank):>10}")

    # ------------------------------------------------------------------
    # 6. LEARNING PATH COMPARISON
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  6. LEARNING PATH: System Scaffold vs Luda's Phases")
    print("=" * 90)
    print(f"\n  System scaffold: {scaffold['total_chapters']} chapters")
    print(f"  Luda's path: 3 phases, {sum(len(p['skills']) for p in LUDA_PHASES)} total skills\n")

    print("  SYSTEM SCAFFOLD:")
    system_skills_in_path = []
    for ch in scaffold["chapters"]:
        skill = ont.get_skill(ch["primary_skill_id"])
        domain = skill["domain"] if skill else "?"
        luda_rank = LUDA_STATE_B.get(ch["primary_skill_id"], {}).get("rank", "—")
        in_luda = ch["primary_skill_id"] in LUDA_STATE_B
        marker = "<<< in Luda's top-10" if in_luda else ""
        print(f"    Ch{ch['chapter_number']}: {ch['primary_skill_id']:<15} "
              f"{ch['primary_skill_name']:<40} "
              f"L{ch['current_level']}->L{ch['target_level']}  "
              f"[{domain}]  {marker}")
        system_skills_in_path.append(ch["primary_skill_id"])

    print(f"\n  LUDA'S LEARNING PATH:")
    luda_all_path_skills = []
    for phase in LUDA_PHASES:
        print(f"    {phase['phase']}")
        for sid in phase["skills"]:
            skill = ont.get_skill(sid)
            name = skill["name"] if skill else "???"
            in_system = sid in system_skills_in_path
            marker = "<<< in system scaffold" if in_system else "    NOT in system scaffold"
            print(f"      {sid:<15} {name:<40} {marker}")
            luda_all_path_skills.append(sid)

    # Coverage analysis
    system_set = set(system_skills_in_path)
    luda_set = set(luda_all_path_skills)
    luda_top10 = set(LUDA_STATE_B.keys())

    overlap = system_set & luda_top10
    system_only = system_set - luda_top10
    luda_only = luda_top10 - system_set

    print(f"\n  COVERAGE ANALYSIS (system scaffold vs Luda's top-10):")
    print(f"    System skills in Luda's top-10:     {len(overlap)}/{len(luda_top10)}  {sorted(overlap)}")
    print(f"    System skills NOT in Luda's top-10: {len(system_only)}  {sorted(system_only)}")
    print(f"    Luda top-10 NOT in system scaffold: {len(luda_only)}  {sorted(luda_only)}")

    # ------------------------------------------------------------------
    # 7. WHY EACH SYSTEM CHAPTER WAS PICKED
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  7. EXPLAINABILITY: Why Each System Chapter Was Selected")
    print("=" * 90)

    for ch in scaffold["chapters"]:
        sid = ch["primary_skill_id"]
        skill = ont.get_skill(sid)
        gap = gap_map.get(sid)
        print(f"\n  Chapter {ch['chapter_number']}: {sid} — {ch['primary_skill_name']}")
        print(f"  {'—' * 60}")
        if gap:
            print(f"    Priority Score:    {gap['priority_score']:.1f}")
            print(f"    Computation:       3*{gap['delta']} + 2*{gap['role_relevance']} - 0.5*{gap['skill_level']} = {gap['priority_score']:.1f}")
            print(f"    Delta:             {gap['delta']} (L{gap['current_level']} -> L{gap['required_level']})")
            print(f"    Role Relevance:    {gap['role_relevance']} ({'target domain' if gap['role_relevance'] else 'non-target domain'})")
            print(f"    Domain:            {gap['domain']}")
            print(f"    Ontology Tier:     L{gap['skill_level']}")
            prereqs = gap.get("prerequisites", [])
            if prereqs:
                print(f"    Prerequisites:     {', '.join(prereqs)}")
            else:
                print(f"    Prerequisites:     none")
        else:
            print(f"    (added via mandatory-category enforcement or top-up)")
            if skill:
                print(f"    Domain:            {skill['domain']}")
                print(f"    Ontology Tier:     L{skill['level']}")

        luda_info = LUDA_STATE_B.get(sid)
        if luda_info:
            print(f"    Luda Rank:         #{luda_info['rank']} ({luda_info['priority']})")
            print(f"    Luda Rationale:    {luda_info['why']}")
        else:
            print(f"    Luda Rank:         NOT in top-10")

    # ------------------------------------------------------------------
    # 8. DISCREPANCIES SUMMARY
    # ------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("  8. DISCREPANCY SUMMARY")
    print("=" * 90)

    discrepancies = []

    # Check system scaffold against Luda's top-10
    for sid, info in sorted(LUDA_STATE_B.items(), key=lambda x: x[1]["rank"]):
        skill = ont.get_skill(sid)
        name = skill["name"] if skill else "???"
        if sid not in system_set:
            gap = gap_map.get(sid)
            if gap:
                reason = (f"In gap list (rank {gaps.index(gap)+1}, score {gap['priority_score']:.1f}) "
                         f"but didn't make the 5-chapter cut. "
                         f"Domain diversity or back-pressure may have excluded it.")
            else:
                reason = "NOT in gap list — check state_b construction or floor logic."
            discrepancies.append({
                "skill": sid,
                "name": name,
                "luda_rank": info["rank"],
                "luda_priority": info["priority"],
                "issue": f"Missing from system scaffold",
                "reason": reason,
            })

    for sid in system_only:
        skill = ont.get_skill(sid)
        name = skill["name"] if skill else "???"
        gap = gap_map.get(sid)
        reason = "Added by mandatory-category enforcement or domain diversity backfill."
        if gap:
            reason = (f"High gap score ({gap['priority_score']:.1f}). "
                     f"The path generator picked it because domain diversity "
                     f"limits (max 2 chapters per domain) displaced other skills.")
        discrepancies.append({
            "skill": sid,
            "name": name,
            "luda_rank": "—",
            "luda_priority": "—",
            "issue": "In system scaffold but NOT in Luda's top-10",
            "reason": reason,
        })

    if discrepancies:
        print(f"\n  Found {len(discrepancies)} discrepancies:\n")
        for i, d in enumerate(discrepancies, 1):
            print(f"  {i}. {d['skill']} — {d['name']}")
            print(f"     Luda: Rank {d['luda_rank']}, Priority: {d['luda_priority']}")
            print(f"     Issue: {d['issue']}")
            print(f"     Why:   {d['reason']}")
            print()
    else:
        print(f"\n  No discrepancies found — system output matches Luda's specification.")

    # ------------------------------------------------------------------
    # 9. RECOMMENDATIONS
    # ------------------------------------------------------------------
    if discrepancies:
        print("=" * 90)
        print("  9. RECOMMENDATIONS TO ALIGN SYSTEM WITH LUDA'S DOCUMENT")
        print("=" * 90)
        print("""
  The system produces 5 chapters per path (by design). Luda's document
  specifies 10 skills across 3 phases (12 weeks). Key architectural
  differences:

  a) System constraint: 5 chapters, max 2 per domain, +1 level per chapter
  b) Luda's vision: 10 skills across 12 weeks, multi-level jumps

  Options to close the gap:
  1. MULTI-PATH: Generate 2-3 sequential 5-chapter paths that together
     cover all 10 skills (aligning with Luda's 3 phases).
  2. PRIORITY OVERRIDE: Allow role templates to force specific skills
     into the scaffold, bypassing domain diversity limits for confirmed
     must-have skills.
  3. PHASE MAPPING: Map Luda's 3 phases to 3 separate scaffold runs,
     each with a focused state_b subset.
""")

    print("=" * 90)
    print("  END OF DIAGNOSTIC REPORT")
    print("=" * 90)


if __name__ == "__main__":
    main()
