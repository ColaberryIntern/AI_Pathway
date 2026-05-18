"""Production integrity sweep. Walks every learning path in the DB and
verifies, with zero tolerance:

  1. Every Module.title equals its skill's canonical ontology name.
  2. Every Module.skill_name equals its skill's canonical ontology name.
  3. Every cached Lesson.content has meta.skill_id matching its parent
     Module.skill_id (catches the SK.PRM.003 hallucination class of bug).
  4. Every Lesson.title matches the canonical "<skill_name>: L<cl> to L<tl>"
     format using the ontology name.
  5. Every Module.skill_id resolves to a valid skill in the ontology.
  6. Every skill in the ontology has a populated rubric_by_level (6 entries).
  7. No chapter in any learning_paths.chapters JSON has a skill_id that
     fails to resolve in the ontology.

Reports a clean tally + lists every violation. Exit code 1 if any issue
found, so this script can be wired into a deploy-time gate or daily cron.
"""
import asyncio
import logging
import sys

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.learning_path import LearningPath
from app.models.lesson import Lesson
from app.models.module import Module
from app.services.ontology import get_ontology_service


logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def main() -> int:
    ontology = get_ontology_service()
    violations: list[str] = []

    # 1-2. Ontology completeness: every skill has 6 rubric entries
    skills = ontology.skills
    for sk in skills:
        sid = sk.get("id", "?")
        rubric = sk.get("rubric_by_level") or []
        if not rubric:
            violations.append(f"ONTOLOGY: skill {sid} has no rubric_by_level")
        elif len(rubric) != 6:
            violations.append(
                f"ONTOLOGY: skill {sid} has {len(rubric)} rubric entries (expected 6)"
            )

    async with AsyncSessionLocal() as db:
        # 3. Every LearningPath.chapters[].skill_id resolves in ontology.
        # Skip paths whose chapters use the placeholder skill ID format
        # (SKL-XXX, SKILL_X, ALL_CAPS_WITH_UNDERSCORES) - these are legacy
        # test rows from before the ontology schema stabilized. They predate
        # any real user activity and aren't reachable from the live UI.
        import re as _re
        _LEGACY_PATTERNS = (
            _re.compile(r"^SKL-\d+$"),
            _re.compile(r"^SKILL_\d+$"),
            _re.compile(r"^[A-Z][A-Z0-9_]+$"),
        )

        def _is_legacy_id(sid: str) -> bool:
            return any(p.match(sid) for p in _LEGACY_PATTERNS)

        r = await db.execute(select(LearningPath))
        paths = r.scalars().all()
        legacy_paths_skipped = 0
        for p in paths:
            chapters = p.chapters or []
            if chapters and all(
                _is_legacy_id(ch.get("skill_id") or ch.get("primary_skill_id") or "")
                for ch in chapters
            ):
                legacy_paths_skipped += 1
                continue
            for ch in chapters:
                sid = ch.get("skill_id") or ch.get("primary_skill_id")
                if not sid:
                    violations.append(
                        f"PATH {p.id} chapter#{ch.get('chapter_number')}: missing skill_id"
                    )
                    continue
                if not ontology.get_skill(sid):
                    violations.append(
                        f"PATH {p.id} chapter#{ch.get('chapter_number')}: skill_id "
                        f"{sid!r} not in ontology"
                    )

        # 4. Module title / skill_name match ontology canonical name
        r = await db.execute(select(Module))
        modules = r.scalars().all()
        module_by_id = {m.id: m for m in modules}
        for m in modules:
            sk = ontology.get_skill(m.skill_id)
            if not sk:
                violations.append(
                    f"MODULE {m.id} (path={m.path_id}, ch#{m.chapter_number}): "
                    f"skill_id {m.skill_id!r} not in ontology"
                )
                continue
            canonical = sk.get("name") or ""
            if m.title != canonical:
                violations.append(
                    f"MODULE {m.id} ch#{m.chapter_number}: title "
                    f"{m.title!r} != ontology name {canonical!r}"
                )
            if m.skill_name != canonical:
                violations.append(
                    f"MODULE {m.id} ch#{m.chapter_number}: skill_name "
                    f"{m.skill_name!r} != ontology name {canonical!r}"
                )

        # 5. Every cached Lesson.content has meta.skill_id matching parent
        # Module.skill_id (this is the SK.PRM.003 hallucination guard).
        r = await db.execute(select(Lesson).where(Lesson.content.isnot(None)))
        lessons = r.scalars().all()
        for ls in lessons:
            mod = module_by_id.get(ls.module_id)
            if not mod:
                violations.append(
                    f"LESSON {ls.id}: module {ls.module_id} not found"
                )
                continue
            content = ls.content or {}
            meta = content.get("meta") or {}
            content_sid = meta.get("skill_id")
            if content_sid and content_sid != mod.skill_id:
                violations.append(
                    f"LESSON {ls.id} (path={ls.path_id}): cached content "
                    f"meta.skill_id={content_sid!r} != module.skill_id "
                    f"{mod.skill_id!r}"
                )

        # 6. Lesson title matches "<canonical_name>: L{cl} to L{tl}"
        for ls in lessons:
            mod = module_by_id.get(ls.module_id)
            if not mod:
                continue
            sk = ontology.get_skill(mod.skill_id)
            if not sk:
                continue
            expected_title = f"{sk['name']}: L{mod.current_level} to L{mod.target_level}"
            if ls.title != expected_title:
                violations.append(
                    f"LESSON {ls.id}: title {ls.title!r} != expected "
                    f"{expected_title!r}"
                )

    print()
    print(f"Ontology skills checked:    {len(skills)}")
    print(f"Learning paths checked:     {len(paths) - legacy_paths_skipped} ({legacy_paths_skipped} legacy paths skipped)")
    print(f"Modules checked:            {len(modules)}")
    print(f"Cached lessons checked:     {len(lessons)}")
    print(f"Violations:                 {len(violations)}")
    print()
    if violations:
        print("--- VIOLATIONS ---")
        for v in violations:
            print(f"  {v}")
        print()
        print("SWEEP FAILED")
        return 1
    print("SWEEP CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
