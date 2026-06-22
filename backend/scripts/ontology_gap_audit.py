"""Ontology gap audit (Trust Before Intelligence - Lexicon / Natural dimension).

Read-only structural audit of backend/app/data/ontology.json to surface where skill
coverage is thin or metadata is missing - the inputs for the Natural +1 ontology-depth
conversation with the SME (Luda). Does NOT change anything.

Run: cd backend && py -3.12 scripts/ontology_gap_audit.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

ONTOLOGY = Path(__file__).resolve().parents[1] / "app" / "data" / "ontology.json"
THIN_DOMAIN_MAX = 3  # domains with <= this many skills are flagged as thin


def main() -> int:
    d = json.loads(ONTOLOGY.read_text(encoding="utf-8"))
    skills = d.get("skills", [])
    domains = {dm["id"]: dm for dm in d.get("domains", [])}
    _scale = d.get("proficiency_scale")
    if isinstance(_scale, list):
        scale_levels = len(_scale) or 6
    elif isinstance(_scale, dict):
        scale_levels = len(_scale.get("levels", []) or []) or 6
    else:
        scale_levels = 6

    by_domain = Counter(s.get("domain", "?") for s in skills)
    skill_ids = {s.get("id") for s in skills}

    empty_rubric = [s["id"] for s in skills if not s.get("rubric_by_level")]
    short_rubric = [
        (s["id"], len(s.get("rubric_by_level") or {}))
        for s in skills
        if s.get("rubric_by_level") and len(s["rubric_by_level"]) < scale_levels
    ]
    no_prereqs = [s["id"] for s in skills if not s.get("prerequisites")]
    orphan_prereqs = []
    for s in skills:
        for p in s.get("prerequisites", []) or []:
            if p not in skill_ids:
                orphan_prereqs.append((s["id"], p))
    domains_no_skills = [did for did in domains if by_domain.get(did, 0) == 0]
    thin_domains = [(did, n) for did, n in by_domain.items() if n <= THIN_DOMAIN_MAX]
    has_description = sum(1 for s in skills if s.get("description"))

    print("=== Ontology gap audit ===")
    print(f"version={d.get('version')} | skills={len(skills)} | domains={len(domains)} "
          f"| proficiency levels={scale_levels}")
    print(f"\nSkills with a `description` field: {has_description}/{len(skills)}")
    print(f"Skills with EMPTY rubric_by_level: {len(empty_rubric)}", empty_rubric[:10])
    print(f"Skills with < {scale_levels} rubric levels: {len(short_rubric)}", short_rubric[:10])
    print(f"Orphan prerequisites (prereq id not a real skill): {len(orphan_prereqs)}",
          orphan_prereqs[:10])
    print(f"Domains with ZERO skills: {len(domains_no_skills)}", domains_no_skills)
    print(f"\nThin domains (<= {THIN_DOMAIN_MAX} skills):")
    for did, n in sorted(thin_domains, key=lambda x: x[1]):
        print(f"  {did:18} {n:>2}  {domains.get(did, {}).get('label', '')}")
    print("\nSkills per domain (all):")
    for did, n in by_domain.most_common():
        print(f"  {did:18} {n:>2}  {domains.get(did, {}).get('label', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
