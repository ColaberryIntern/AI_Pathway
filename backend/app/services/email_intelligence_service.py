"""Email Intelligence Service - AI classification and extraction.

Uses the existing LLM provider to classify email intent, extract
topics, todos, priority, and owners from email content.
"""
import json
import logging
from dataclasses import dataclass, field

from app.models.email_thread import EmailThread
from app.services.llm import get_llm_provider

logger = logging.getLogger(__name__)

CLASSIFICATION_SYSTEM_PROMPT = """You are an email intelligence analyst. Given an email, you must:

1. Classify the email type: "project" (work requiring deliverables), "task" (specific action items),
   or "discussion" (information sharing, no action needed).
2. Extract a concise topic title (max 10 words).
3. Determine priority: "high" (urgent, blocker, deadline), "medium" (important but not urgent),
   "low" (informational, FYI).
4. Extract 3-7 actionable todos. Each todo must be:
   - A concrete, actionable step (start with a verb)
   - Assignable to a person
   - Measurable (has a clear done state)
   - Convert vague language into specific actions
5. Identify owners (people who need to act).
6. Assign a confidence score (0.0-1.0) for your classification.

RULES:
- If the email is purely informational with no action items, set type="discussion" and todos=[]
- Maximum 7 todos per email
- Minimum 3 todos if the email contains actionable content
- Normalize vague requests: "look into X" becomes "Research X and summarize findings"
- Extract implicit tasks: "we need to..." becomes an explicit todo

Return ONLY a JSON object with this exact structure:
{
  "topic": "string - concise topic title",
  "type": "project" | "task" | "discussion",
  "priority": "high" | "medium" | "low",
  "todos": ["string - actionable todo 1", "string - actionable todo 2"],
  "owners": ["string - person name or email"],
  "confidence": 0.85
}"""


@dataclass
class ClassifiedEmail:
    """Result of email classification and extraction."""
    topic: str = ""
    type: str = "discussion"
    priority: str = "medium"
    todos: list[str] = field(default_factory=list)
    owners: list[str] = field(default_factory=list)
    confidence: float = 0.0


async def classify_and_extract(email: EmailThread) -> ClassifiedEmail:
    """Classify an email and extract actionable items using LLM.

    Returns a ClassifiedEmail with topic, type, priority, todos, and owners.
    """
    llm = get_llm_provider()

    prompt = f"""Analyze this email:

FROM: {email.sender}
TO: {', '.join(email.recipients or [])}
SUBJECT: {email.subject}
DATE: {email.timestamp.isoformat() if email.timestamp else 'unknown'}

BODY:
{email.body[:3000]}

Extract the topic, type, priority, actionable todos, and owners."""

    try:
        response = await llm.generate(
            prompt=prompt,
            system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
            max_tokens=1024,
            temperature=0.2,
            json_mode=True,
        )
        data = json.loads(response.content)
        return ClassifiedEmail(
            topic=data.get("topic", email.subject[:50]),
            type=data.get("type", "discussion"),
            priority=data.get("priority", "medium"),
            todos=data.get("todos", [])[:7],
            owners=data.get("owners", []),
            confidence=float(data.get("confidence", 0.5)),
        )
    except Exception as e:
        logger.error("Email classification failed: %s", e)
        return ClassifiedEmail(
            topic=email.subject[:50],
            type="discussion",
            priority="medium",
            confidence=0.0,
        )
