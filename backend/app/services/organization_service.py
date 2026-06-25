"""Organization service (multi-tenancy, increment 1).

Holds the startup backfill and the pure progress-aggregation used by the
enterprise "who is doing what" dashboard. The aggregation is a pure function so
it is unit-tested without a DB.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, text

from app.models.organization import DEFAULT_ORG_ID, DEFAULT_ORG_NAME, Organization
from app.models.user import User


async def ensure_default_org_and_backfill(db) -> dict:
    """Create the default organization if missing and assign it to any user
    with a null org_id. Idempotent: safe to run on every startup.

    Returns a small summary for logging.
    """
    existing = (await db.execute(
        select(Organization).where(Organization.id == DEFAULT_ORG_ID)
    )).scalars().first()
    created = False
    if not existing:
        db.add(Organization(id=DEFAULT_ORG_ID, name=DEFAULT_ORG_NAME))
        await db.commit()
        created = True

    # Backfill users missing an org. Raw UPDATE keeps it a single statement and
    # avoids loading every user row.
    result = await db.execute(
        text("UPDATE users SET org_id = :oid WHERE org_id IS NULL"),
        {"oid": DEFAULT_ORG_ID},
    )
    await db.commit()
    return {"default_org_created": created, "users_backfilled": result.rowcount or 0}


def summarize_learner_paths(
    paths: list[Any],
    progress_by_path: dict[str, Any],
) -> dict:
    """Aggregate one learner's path progress. Pure - no DB.

    `paths` is a list of objects with .id, .title, .total_chapters, .created_at.
    `progress_by_path` maps path_id -> a progress object with .chapter_status
    (a dict of chapter -> status) or None.
    """
    active: list[dict] = []
    completed: list[dict] = []
    total_skills = 0

    for path in paths:
        progress = progress_by_path.get(path.id)
        chapter_status = getattr(progress, "chapter_status", None) or {} if progress else {}
        completed_chapters = sum(1 for s in chapter_status.values() if s == "completed")
        total_chapters = path.total_chapters or 0
        pct = round(completed_chapters / total_chapters * 100, 1) if total_chapters > 0 else 0.0
        entry = {
            "id": path.id,
            "title": path.title,
            "total_chapters": total_chapters,
            "completed_chapters": completed_chapters,
            "completion_percentage": pct,
        }
        if total_chapters > 0 and completed_chapters == total_chapters:
            completed.append(entry)
            total_skills += total_chapters
        else:
            active.append(entry)

    total_chapters_all = sum(e["total_chapters"] for e in active + completed)
    completed_all = sum(e["completed_chapters"] for e in active + completed)
    overall_pct = round(completed_all / total_chapters_all * 100, 1) if total_chapters_all > 0 else 0.0

    return {
        "total_paths": len(paths),
        "active_paths": active,
        "completed_paths": completed,
        "total_skills_learned": total_skills,
        "overall_completion_percentage": overall_pct,
    }
