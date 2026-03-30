"""Communication Feedback Service - execution tracking.

Monitors todo completion rates, recurring topics, and stalled execution
to surface bottlenecks and insights.
"""
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communication_feedback import CommunicationFeedback
from app.models.topic_thread_map import TopicThreadMap
from app.models.email_thread import EmailThread

logger = logging.getLogger(__name__)


async def get_or_create_feedback(
    db: AsyncSession, topic_thread_map_id: str
) -> CommunicationFeedback:
    """Get or create a feedback record for a topic mapping."""
    result = await db.execute(
        select(CommunicationFeedback).where(
            CommunicationFeedback.topic_thread_map_id == topic_thread_map_id
        )
    )
    feedback = result.scalars().first()
    if not feedback:
        feedback = CommunicationFeedback(
            topic_thread_map_id=topic_thread_map_id,
        )
        db.add(feedback)
        await db.flush()
    return feedback


async def update_feedback(
    db: AsyncSession,
    topic_thread_map_id: str,
    todos_created: int = 0,
) -> None:
    """Update feedback after processing an email."""
    feedback = await get_or_create_feedback(db, topic_thread_map_id)
    feedback.todos_created += todos_created
    feedback.last_activity = datetime.utcnow()

    # Check for recurrence
    result = await db.execute(
        select(func.count(EmailThread.id))
        .join(TopicThreadMap, EmailThread.thread_id == TopicThreadMap.email_thread_id)
        .where(TopicThreadMap.id == topic_thread_map_id)
    )
    count = result.scalar() or 0
    if count >= 3:
        feedback.is_recurring = True
        feedback.recurrence_count = count


async def get_bottlenecks(db: AsyncSession) -> list[dict]:
    """Get stalled topics (open > 7 days with no completion)."""
    cutoff = datetime.utcnow() - timedelta(days=7)
    result = await db.execute(
        select(CommunicationFeedback, TopicThreadMap)
        .join(TopicThreadMap, CommunicationFeedback.topic_thread_map_id == TopicThreadMap.id)
        .where(
            CommunicationFeedback.todos_completed == 0,
            CommunicationFeedback.todos_created > 0,
            CommunicationFeedback.last_activity < cutoff,
        )
    )
    rows = result.all()
    return [
        {
            "topic_thread_map_id": fb.topic_thread_map_id,
            "basecamp_topic_id": mapping.basecamp_topic_id,
            "todos_created": fb.todos_created,
            "days_stalled": (datetime.utcnow() - fb.last_activity).days,
        }
        for fb, mapping in rows
    ]


async def get_recurring_topics(db: AsyncSession) -> list[dict]:
    """Get topics that keep recurring (3+ emails on same thread)."""
    result = await db.execute(
        select(CommunicationFeedback, TopicThreadMap)
        .join(TopicThreadMap, CommunicationFeedback.topic_thread_map_id == TopicThreadMap.id)
        .where(CommunicationFeedback.is_recurring == True)
    )
    rows = result.all()
    return [
        {
            "topic_thread_map_id": fb.topic_thread_map_id,
            "basecamp_topic_id": mapping.basecamp_topic_id,
            "recurrence_count": fb.recurrence_count,
        }
        for fb, mapping in rows
    ]


async def get_summary_stats(db: AsyncSession) -> dict:
    """Get overall communication pipeline stats."""
    total_emails = await db.execute(select(func.count(EmailThread.id)))
    processed = await db.execute(
        select(func.count(EmailThread.id)).where(EmailThread.processed == True)
    )
    active_topics = await db.execute(
        select(func.count(TopicThreadMap.id)).where(TopicThreadMap.status == "active")
    )
    total_todos = await db.execute(
        select(func.coalesce(func.sum(CommunicationFeedback.todos_created), 0))
    )
    completed_todos = await db.execute(
        select(func.coalesce(func.sum(CommunicationFeedback.todos_completed), 0))
    )

    return {
        "total_emails_ingested": total_emails.scalar() or 0,
        "emails_processed": processed.scalar() or 0,
        "active_topics": active_topics.scalar() or 0,
        "total_todos_created": total_todos.scalar() or 0,
        "total_todos_completed": completed_todos.scalar() or 0,
    }
