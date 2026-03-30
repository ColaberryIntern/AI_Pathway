"""Communication Orchestrator - main pipeline coordinator.

Connects all communication intelligence services into a single
idempotent pipeline: ingest -> classify -> prioritize -> resolve
-> generate todos -> sync to Basecamp -> update feedback.
"""
import logging
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_thread import EmailThread
from app.services.email_ingestion_service import fetch_new_emails, get_unprocessed
from app.services.email_intelligence_service import classify_and_extract
from app.services.priority_engine import score_email, should_process
from app.services.thread_resolution_service import resolve_thread, create_mapping
from app.services.todo_generation_service import generate_structured_todos
from app.services import basecamp_service
from app.services.communication_feedback_service import update_feedback

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result of a pipeline run."""
    emails_ingested: int = 0
    emails_processed: int = 0
    emails_skipped: int = 0
    topics_created: int = 0
    topics_updated: int = 0
    todos_created: int = 0
    errors: list[str] = field(default_factory=list)


async def run_ingestion(db: AsyncSession, lookback_hours: int = 24) -> int:
    """Step 1: Fetch new emails from Gmail and store in DB."""
    try:
        new_emails = await fetch_new_emails(db, lookback_hours=lookback_hours)
        return len(new_emails)
    except Exception as e:
        logger.error("Email ingestion failed: %s", e)
        raise


async def run_pipeline(db: AsyncSession) -> PipelineResult:
    """Run the full processing pipeline on unprocessed emails.

    This is idempotent: re-running on already-processed emails is a no-op.
    """
    result = PipelineResult()
    emails = await get_unprocessed(db)

    if not emails:
        logger.info("No unprocessed emails to process")
        return result

    logger.info("Processing %d unprocessed emails", len(emails))

    for email in emails:
        try:
            await _process_single_email(db, email, result)
        except Exception as e:
            error_msg = f"Failed to process email {email.message_id}: {e}"
            logger.error(error_msg, exc_info=True)
            result.errors.append(error_msg)
            # Don't mark as processed so it can be retried
            continue

    await db.commit()
    logger.info(
        "Pipeline complete: %d processed, %d skipped, %d topics created, "
        "%d topics updated, %d todos created, %d errors",
        result.emails_processed, result.emails_skipped,
        result.topics_created, result.topics_updated,
        result.todos_created, len(result.errors),
    )
    return result


async def _process_single_email(
    db: AsyncSession, email: EmailThread, result: PipelineResult
) -> None:
    """Process a single email through the full pipeline."""

    # Step 2: Classify with AI
    classified = await classify_and_extract(email)
    email.classified_data = {
        "topic": classified.topic,
        "type": classified.type,
        "priority": classified.priority,
        "todos": classified.todos,
        "owners": classified.owners,
        "confidence": classified.confidence,
    }

    # Step 3: Priority check
    priority_score = score_email(email, classified)
    if not should_process(priority_score):
        email.processed = True
        email.skipped = True
        result.emails_skipped += 1
        logger.info(
            "Skipped low-priority email: %s (score: %.1f)",
            email.subject[:50], priority_score,
        )
        return

    # Step 4: Thread resolution
    mapping = await resolve_thread(db, email.thread_id)

    if mapping:
        # Existing thread - append to Basecamp topic
        try:
            await basecamp_service.append_comment(
                mapping.basecamp_topic_id,
                f"<strong>From:</strong> {email.sender}<br>"
                f"<strong>Date:</strong> {email.timestamp}<br><br>"
                f"{email.body[:2000]}",
            )
            result.topics_updated += 1
        except Exception as e:
            logger.warning("Failed to append to Basecamp topic: %s", e)

        # Add new todos if any
        if classified.todos:
            todos = await generate_structured_todos(classified)
            if todos and mapping.basecamp_todolist_id:
                try:
                    todo_contents = [t.content for t in todos]
                    await basecamp_service.add_todos(
                        mapping.basecamp_todolist_id, todo_contents
                    )
                    result.todos_created += len(todos)
                    await update_feedback(
                        db, mapping.id, todos_created=len(todos)
                    )
                except Exception as e:
                    logger.warning("Failed to add todos to Basecamp: %s", e)

    else:
        # New thread - create Basecamp topic + todolist
        try:
            topic_id = await basecamp_service.create_topic(
                title=classified.topic,
                content=(
                    f"<strong>From:</strong> {email.sender}<br>"
                    f"<strong>Subject:</strong> {email.subject}<br>"
                    f"<strong>Priority:</strong> {classified.priority}<br><br>"
                    f"{email.body[:2000]}"
                ),
            )
            result.topics_created += 1

            todolist_id = None
            if classified.todos:
                todos = await generate_structured_todos(classified)
                if todos:
                    todolist_id = await basecamp_service.create_todo_list(
                        title=f"Tasks: {classified.topic[:50]}",
                    )
                    todo_contents = [t.content for t in todos]
                    await basecamp_service.add_todos(todolist_id, todo_contents)
                    result.todos_created += len(todos)

            new_mapping = await create_mapping(
                db, email.thread_id, topic_id, todolist_id
            )
            await update_feedback(
                db, new_mapping.id, todos_created=result.todos_created
            )

        except Exception as e:
            logger.error("Failed to create Basecamp topic: %s", e)
            raise

    # Mark as processed
    email.processed = True
    result.emails_processed += 1
