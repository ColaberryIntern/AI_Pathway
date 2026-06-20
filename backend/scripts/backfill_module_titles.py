"""Backfill: rewrite existing Module.title, Module.skill_name, and the
corresponding Lesson.title for every learning path so the dashboard
sidebar shows the canonical ontology skill name instead of whatever the
path-generator LLM made up.

Idempotent: skips modules already aligned.
"""
import asyncio
import logging

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.lesson import Lesson
from app.models.module import Module
from app.services.ontology import get_ontology_service


logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


async def main() -> None:
    ontology = get_ontology_service()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Module))
        modules = result.scalars().all()

        rewritten = 0
        lessons_rewritten = 0
        skipped_no_skill = 0
        skipped_aligned = 0

        for module in modules:
            sk = ontology.get_skill(module.skill_id) if module.skill_id else None
            if not sk or not sk.get("name"):
                skipped_no_skill += 1
                continue
            canonical_name = sk["name"]

            module_changed = False
            if module.skill_name != canonical_name:
                module.skill_name = canonical_name
                module_changed = True
            if module.title != canonical_name:
                module.title = canonical_name
                module_changed = True

            # Realign Lesson.title to "<canonical_name>: L{cl} to L{tl}"
            r = await db.execute(select(Lesson).where(Lesson.module_id == module.id))
            for lesson in r.scalars().all():
                new_title = f"{canonical_name}: L{module.current_level} to L{module.target_level}"
                if lesson.title != new_title:
                    lesson.title = new_title
                    lessons_rewritten += 1

            # Realign lesson_outline JSON inside the Module record
            if module.lesson_outline:
                outline_changed = False
                for entry in module.lesson_outline:
                    new_t = f"{canonical_name}: L{module.current_level} to L{module.target_level}"
                    if entry.get("title") != new_t:
                        entry["title"] = new_t
                        outline_changed = True
                if outline_changed:
                    # SQLAlchemy needs the JSON field marked dirty
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(module, "lesson_outline")
                    module_changed = True

            if module_changed:
                rewritten += 1
            else:
                skipped_aligned += 1

        await db.commit()

        print(f"Modules processed:     {len(modules)}")
        print(f"  rewritten:           {rewritten}")
        print(f"  already aligned:     {skipped_aligned}")
        print(f"  skill not in onto:   {skipped_no_skill}")
        print(f"Lesson titles rewritten: {lessons_rewritten}")


if __name__ == "__main__":
    asyncio.run(main())
