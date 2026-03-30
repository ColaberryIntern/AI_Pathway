"""Communication Intelligence API routes.

Endpoints for email ingestion, pipeline processing, thread management,
daily summaries, and execution feedback.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_database
from app.models.email_thread import EmailThread
from app.models.topic_thread_map import TopicThreadMap
from app.services.communication_orchestrator import run_ingestion, run_pipeline
from app.services.daily_summary_service import generate_summary
from app.services.communication_feedback_service import (
    get_bottlenecks,
    get_recurring_topics,
    get_summary_stats,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest")
async def trigger_ingestion(
    lookback_hours: int = 24,
    db: AsyncSession = Depends(get_database),
):
    """Manually trigger email ingestion from Gmail.

    Fetches emails from monitored senders within the lookback window
    and stores them in the database.
    """
    try:
        count = await run_ingestion(db, lookback_hours=lookback_hours)
        return {"ingested": count, "message": f"Ingested {count} new emails"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/process")
async def trigger_processing(
    db: AsyncSession = Depends(get_database),
):
    """Run the full processing pipeline on unprocessed emails.

    Classifies emails, checks priority, resolves threads,
    generates todos, and syncs to Basecamp.
    """
    try:
        result = await run_pipeline(db)
        return {
            "emails_processed": result.emails_processed,
            "emails_skipped": result.emails_skipped,
            "topics_created": result.topics_created,
            "topics_updated": result.topics_updated,
            "todos_created": result.todos_created,
            "errors": result.errors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/run")
async def trigger_full_run(
    lookback_hours: int = 24,
    db: AsyncSession = Depends(get_database),
):
    """Run both ingestion and processing in one call."""
    try:
        ingested = await run_ingestion(db, lookback_hours=lookback_hours)
        result = await run_pipeline(db)
        return {
            "ingested": ingested,
            "emails_processed": result.emails_processed,
            "emails_skipped": result.emails_skipped,
            "topics_created": result.topics_created,
            "topics_updated": result.topics_updated,
            "todos_created": result.todos_created,
            "errors": result.errors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@router.get("/threads")
async def list_threads(
    db: AsyncSession = Depends(get_database),
):
    """List all tracked email threads with their Basecamp mappings."""
    result = await db.execute(
        select(EmailThread)
        .order_by(EmailThread.timestamp.desc())
        .limit(100)
    )
    emails = result.scalars().all()

    threads = []
    for e in emails:
        # Get linked Basecamp topic
        mapping_result = await db.execute(
            select(TopicThreadMap).where(
                TopicThreadMap.email_thread_id == e.thread_id
            )
        )
        mapping = mapping_result.scalars().first()

        threads.append({
            "id": e.id,
            "thread_id": e.thread_id,
            "message_id": e.message_id,
            "sender": e.sender,
            "subject": e.subject,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "processed": e.processed,
            "skipped": e.skipped,
            "classified_data": e.classified_data,
            "basecamp_topic_id": mapping.basecamp_topic_id if mapping else None,
            "basecamp_status": mapping.status if mapping else None,
        })

    return threads


@router.get("/threads/{thread_id}")
async def get_thread_detail(
    thread_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get detailed view of a specific email thread."""
    result = await db.execute(
        select(EmailThread).where(EmailThread.thread_id == thread_id)
        .order_by(EmailThread.timestamp.asc())
    )
    emails = list(result.scalars().all())

    if not emails:
        raise HTTPException(status_code=404, detail="Thread not found")

    mapping_result = await db.execute(
        select(TopicThreadMap).where(
            TopicThreadMap.email_thread_id == thread_id
        )
    )
    mapping = mapping_result.scalars().first()

    return {
        "thread_id": thread_id,
        "messages": [
            {
                "id": e.id,
                "sender": e.sender,
                "subject": e.subject,
                "body": e.body[:1000],
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "processed": e.processed,
                "classified_data": e.classified_data,
            }
            for e in emails
        ],
        "basecamp": {
            "topic_id": mapping.basecamp_topic_id,
            "todolist_id": mapping.basecamp_todolist_id,
            "status": mapping.status,
        } if mapping else None,
    }


@router.get("/summary")
async def get_daily_summary(
    db: AsyncSession = Depends(get_database),
):
    """Generate a daily execution summary."""
    try:
        summary = await generate_summary(db)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.get("/feedback")
async def get_feedback(
    db: AsyncSession = Depends(get_database),
):
    """Get execution feedback: stats, bottlenecks, and recurring topics."""
    stats = await get_summary_stats(db)
    bottlenecks = await get_bottlenecks(db)
    recurring = await get_recurring_topics(db)

    return {
        "stats": stats,
        "bottlenecks": bottlenecks,
        "recurring_topics": recurring,
    }
