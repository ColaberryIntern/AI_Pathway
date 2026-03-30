"""Todo Generation Service - converts extracted data into atomic todos.

Takes raw todo strings from the email intelligence service and refines
them into actionable, assignable, measurable steps.
"""
import json
import logging
from dataclasses import dataclass

from app.services.email_intelligence_service import ClassifiedEmail
from app.services.llm import get_llm_provider

logger = logging.getLogger(__name__)


@dataclass
class StructuredTodo:
    """A refined, actionable todo item."""
    content: str
    assignee: str | None = None
    priority: str = "medium"  # high | medium | low
    depends_on: int | None = None  # index of dependency (soft ordering)


REFINEMENT_PROMPT = """You are a task refinement engine. Given a list of raw todos extracted from
an email, refine them into atomic, actionable steps.

Each todo must:
- Start with an action verb (Create, Update, Review, Send, etc.)
- Be completable by one person
- Have a clear done state
- Be specific enough to act on without re-reading the email

If a todo is too complex, break it into 2-3 sub-steps.
If a todo is already clear, keep it as-is.

Return a JSON array of objects:
[
  {"content": "Action verb + specific task", "assignee": "person or null", "priority": "high|medium|low"}
]"""


async def generate_structured_todos(
    classified: ClassifiedEmail,
) -> list[StructuredTodo]:
    """Convert raw extracted todos into structured, actionable items.

    For simple todos (already actionable), returns them directly.
    For complex ones, uses LLM to refine into atomic steps.
    """
    if not classified.todos:
        return []

    # If todos are already simple and actionable, skip LLM refinement
    if len(classified.todos) <= 3 and all(
        len(t.split()) >= 3 and t[0].isupper() for t in classified.todos
    ):
        return [
            StructuredTodo(
                content=t,
                assignee=classified.owners[0] if classified.owners else None,
                priority=classified.priority,
            )
            for t in classified.todos
        ]

    # Use LLM to refine complex todos
    llm = get_llm_provider()
    try:
        prompt = f"""Refine these raw todos into atomic, actionable steps:

Raw todos:
{json.dumps(classified.todos, indent=2)}

Topic: {classified.topic}
Priority: {classified.priority}
Owners: {', '.join(classified.owners) if classified.owners else 'Not specified'}"""

        response = await llm.generate(
            prompt=prompt,
            system_prompt=REFINEMENT_PROMPT,
            max_tokens=1024,
            temperature=0.2,
            json_mode=True,
        )
        items = json.loads(response.content)
        return [
            StructuredTodo(
                content=item.get("content", ""),
                assignee=item.get("assignee"),
                priority=item.get("priority", classified.priority),
            )
            for item in items
            if item.get("content")
        ][:7]  # Cap at 7

    except Exception as e:
        logger.warning("Todo refinement failed, using raw todos: %s", e)
        return [
            StructuredTodo(
                content=t,
                assignee=classified.owners[0] if classified.owners else None,
                priority=classified.priority,
            )
            for t in classified.todos
        ]
