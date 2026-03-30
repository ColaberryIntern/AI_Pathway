"""Daily Summary Service - generates execution digest.

Produces a structured daily summary of active topics, pending todos,
blocked items, recurring issues, and suggested focus areas.
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.communication_feedback_service import (
    get_bottlenecks,
    get_recurring_topics,
    get_summary_stats,
)
from app.services.llm import get_llm_provider

logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT = """You are an executive communication analyst. Generate a concise
daily execution summary from the provided data.

Format your response as clean markdown with these sections:
## Daily Execution Summary

### Active Topics
- List active topics with status

### Pending Todos
- Count and highlight blocked items

### Recurring Issues
- Flag topics that keep coming back

### Suggested Focus Areas
- Top 3 priorities for today based on the data

Be concise. No filler. Focus on actionable insights."""


async def generate_summary(db: AsyncSession) -> str:
    """Generate a daily execution summary using LLM.

    Combines stats, bottlenecks, and recurring topics into
    a structured markdown digest.
    """
    stats = await get_summary_stats(db)
    bottlenecks = await get_bottlenecks(db)
    recurring = await get_recurring_topics(db)

    context = f"""Communication Pipeline Stats:
- Total emails ingested: {stats['total_emails_ingested']}
- Emails processed: {stats['emails_processed']}
- Active topics: {stats['active_topics']}
- Todos created: {stats['total_todos_created']}
- Todos completed: {stats['total_todos_completed']}

Bottlenecks (stalled > 7 days):
{_format_bottlenecks(bottlenecks)}

Recurring Topics (3+ emails):
{_format_recurring(recurring)}"""

    llm = get_llm_provider()
    try:
        response = await llm.generate(
            prompt=f"Generate a daily execution summary from this data:\n\n{context}",
            system_prompt=SUMMARY_SYSTEM_PROMPT,
            max_tokens=1024,
            temperature=0.3,
        )
        return response.content
    except Exception as e:
        logger.error("Summary generation failed: %s", e)
        return f"## Daily Summary\n\nGeneration failed: {e}\n\n### Raw Stats\n{context}"


def _format_bottlenecks(bottlenecks: list[dict]) -> str:
    if not bottlenecks:
        return "None"
    lines = []
    for b in bottlenecks:
        lines.append(f"- Topic {b['basecamp_topic_id']}: {b['todos_created']} todos, stalled {b['days_stalled']} days")
    return "\n".join(lines)


def _format_recurring(recurring: list[dict]) -> str:
    if not recurring:
        return "None"
    lines = []
    for r in recurring:
        lines.append(f"- Topic {r['basecamp_topic_id']}: {r['recurrence_count']} occurrences")
    return "\n".join(lines)
