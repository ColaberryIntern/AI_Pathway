"""Thread Resolution Service - maintains email-to-Basecamp continuity.

Ensures that replies in the same email thread append to the existing
Basecamp topic instead of creating duplicate topics.
"""
import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_thread_map import TopicThreadMap

logger = logging.getLogger(__name__)


async def resolve_thread(
    db: AsyncSession, email_thread_id: str
) -> TopicThreadMap | None:
    """Check if a Basecamp topic already exists for this email thread.

    Returns the mapping if found, None if this is a new thread.
    """
    result = await db.execute(
        select(TopicThreadMap).where(
            TopicThreadMap.email_thread_id == email_thread_id
        )
    )
    return result.scalars().first()


async def create_mapping(
    db: AsyncSession,
    email_thread_id: str,
    basecamp_topic_id: str,
    basecamp_todolist_id: str | None = None,
) -> TopicThreadMap:
    """Create a new email-thread-to-Basecamp mapping."""
    mapping = TopicThreadMap(
        email_thread_id=email_thread_id,
        basecamp_topic_id=basecamp_topic_id,
        basecamp_todolist_id=basecamp_todolist_id,
        status="active",
    )
    db.add(mapping)
    await db.flush()
    logger.info(
        "Created thread mapping: %s -> topic %s",
        email_thread_id, basecamp_topic_id,
    )
    return mapping


async def update_mapping_status(
    db: AsyncSession,
    mapping: TopicThreadMap,
    status: str,
) -> None:
    """Update the status of a thread mapping."""
    mapping.status = status
    mapping.last_updated = datetime.utcnow()
    await db.flush()
