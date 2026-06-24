"""Ontology cleanup audit (READ-ONLY).

Jun 23 weekly sync: the ontology has grown to ~220 skills with "remnants of
different things we put in and then took out." Luda wants it cleaned up so it is
"not all over the place." Removing ontology nodes is destructive, Gate-1/Gate-2
gated, and an IP/content judgment owned by Luda + Vivek - so this script does NOT
delete anything. It produces the candidate list + blast radius so the owners can
decide what to prune safely.

What it reports (all read-only):
  - Structural hygiene: skills missing a 6-level rubric_by_level, duplicate
    names/ids, domains with no skills, skill domains not defined.
  - Usage: which ontology skills are referenced by any Module / cached Lesson in
    the DB vs. ORPHANS (never used) -> prune candidates.
  - Integrity: skill_ids used by modules/lessons that are NOT in the ontology
    (these would fail the demo integrity sweep).

Usage (inside ai-pathway-backend-1, against prod DB):
    python /app/ontology_cleanup_audit.py
Outputs a JSON blob between AUDIT_JSON markers for capture.
"""
import asyncio
import collections
import json
import logging
from pathlib import Path

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def load_ontology() -> dict:
    for cand in (Path("/app/app/data/ontology.json"),
                 Path("backend/app/data/ontology.json"),
                 Path("app/data/ontology.json")):
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
    raise FileNotFoundError("ontology.json not found")


def structural_findings(skills: list, domains: list) -> dict:
    miss_rbl = [s["id"] for s in skills if not s.get("rubric_by_level")
                or len(s.get("rubric_by_level") or {}) < 6]
    names = collections.Counter((s.get("name") or "").strip().lower() for s in skills)
    dup_names = [n for n, c in names.items() if c > 1 and n]
    ids = collections.Counter(s["id"] for s in skills)
    dup_ids = [i for i, c in ids.items() if c > 1]
    dom_def = {d["id"] for d in domains}
    dom_used = collections.Counter(s.get("domain") for s in skills)
    return {
        "missing_or_thin_rubric_by_level": miss_rbl,
        "duplicate_names": dup_names,
        "duplicate_ids": dup_ids,
        "domains_with_zero_skills": sorted(dom_def - set(dom_used)),
        "skill_domains_not_defined": sorted(set(dom_used) - dom_def),
        "skills_per_domain": dict(sorted(dom_used.items())),
    }


async def usage_findings(valid_ids: set) -> dict:
    """Which ontology skills are referenced by Modules / cached Lessons."""
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.lesson import Lesson
    from app.models.module import Module

    used = set()
    module_ref = collections.Counter()
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(Module.skill_id))
        for (sid,) in r.all():
            if sid:
                used.add(sid)
                module_ref[sid] += 1
        r = await db.execute(select(Lesson).where(Lesson.content.isnot(None)))
        for ls in r.scalars().all():
            meta = (ls.content or {}).get("meta") or {}
            sid = meta.get("skill_id")
            if sid:
                used.add(sid)
    orphans = sorted(valid_ids - used)
    used_not_in_ontology = sorted(used - valid_ids)
    return {
        "used_skill_count": len(used & valid_ids),
        "orphan_skill_count": len(orphans),
        "orphan_skill_ids": orphans,
        "used_skill_ids_not_in_ontology": used_not_in_ontology,
        "top_referenced": module_ref.most_common(15),
    }


async def main():
    ont = load_ontology()
    skills = ont["skills"]
    domains = ont["domains"]
    valid_ids = {s["id"] for s in skills}

    report = {
        "ontology_version": ont.get("version"),
        "total_skills": len(skills),
        "total_domains": len(domains),
        "structural": structural_findings(skills, domains),
    }
    try:
        report["usage"] = await usage_findings(valid_ids)
    except Exception as e:
        report["usage"] = {"error": f"DB usage analysis unavailable: {e}"}

    print("AUDIT_JSON_START")
    print(json.dumps(report, indent=2))
    print("AUDIT_JSON_END")


if __name__ == "__main__":
    asyncio.run(main())
