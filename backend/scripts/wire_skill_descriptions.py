"""Wire approved skill descriptions into ontology.json (lands Natural 4 -> 5).

Once Luda has reviewed/edited docs/compliance/skill_descriptions_draft.json, this
writes each approved description into the matching skill's `description` field in
ontology.json. Code that reads skill.get("description") (rubric_scorer,
linkedin_parser, the analysis enrich step, Top-5 tooltips) then has real content.

Safe by default:
  - DRY-RUN unless --apply is passed (prints the match report, writes nothing).
  - --apply backs up ontology.json first, then writes (preserving structure + order).
  - Pure wire_descriptions() core is unit-tested; idempotent.

Run (review):  cd backend && py -3.12 scripts/wire_skill_descriptions.py
Run (commit):  cd backend && py -3.12 scripts/wire_skill_descriptions.py --apply
Optional:      --descriptions <path>   (default: the draft json)

AFTER --apply: ontology.json changed -> per CLAUDE.md re-run Gate 1 (sweep_integrity)
and Gate 2 (verify_profile_e2e) before any customer demo. Descriptions are additive
(no id/rubric/structure change) so cached lesson content is unaffected.
"""
import argparse
import copy
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY = ROOT / "backend" / "app" / "data" / "ontology.json"
DEFAULT_DESCS = ROOT / "docs" / "compliance" / "skill_descriptions_draft.json"


def wire_descriptions(ontology: dict, descriptions: dict) -> tuple[dict, dict]:
    """Pure: return (new_ontology, report). Sets skill['description'] from
    descriptions[id] for every matching skill. Does not mutate the input."""
    out = copy.deepcopy(ontology)
    skills = out.get("skills", [])
    skill_ids = {s.get("id") for s in skills}
    matched = 0
    for s in skills:
        desc = descriptions.get(s.get("id"))
        if desc:
            s["description"] = desc.strip()
            matched += 1
    report = {
        "total_skills": len(skills),
        "matched": matched,
        "missing_description": sorted(sid for sid in skill_ids if sid not in descriptions),
        "orphan_descriptions": sorted(k for k in descriptions if k not in skill_ids),
    }
    return out, report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write ontology.json (else dry-run)")
    ap.add_argument("--descriptions", default=str(DEFAULT_DESCS))
    args = ap.parse_args()

    ontology = json.loads(ONTOLOGY.read_text(encoding="utf-8"))
    descriptions = json.loads(Path(args.descriptions).read_text(encoding="utf-8"))
    new_ontology, report = wire_descriptions(ontology, descriptions)

    print("=== wire_skill_descriptions ===")
    print(f"skills={report['total_skills']} matched={report['matched']} "
          f"missing={len(report['missing_description'])} orphans={len(report['orphan_descriptions'])}")
    if report["missing_description"]:
        print("  skills WITHOUT a description:", report["missing_description"][:12])
    if report["orphan_descriptions"]:
        print("  descriptions with NO matching skill:", report["orphan_descriptions"][:12])

    if not args.apply:
        print("\nDRY-RUN (no file written). Re-run with --apply to commit.")
        return 0

    backup = ONTOLOGY.with_suffix(f".json.bak.{int(time.time())}")
    backup.write_text(json.dumps(ontology, indent=2, ensure_ascii=False), encoding="utf-8")
    ONTOLOGY.write_text(json.dumps(new_ontology, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nAPPLIED. backup={backup.name}")
    print("NEXT: re-run Gate 1 (sweep_integrity) + Gate 2 (verify_profile_e2e) before any demo; "
          "redeploy backend so the tooltips/judge see the descriptions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
