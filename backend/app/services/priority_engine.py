"""Priority Engine - scores and filters emails by importance.

Emails below the threshold are skipped and not converted to
Basecamp items, reducing noise.
"""
import re
from app.models.email_thread import EmailThread
from app.services.email_intelligence_service import ClassifiedEmail

# Configurable weights
SENDER_WEIGHTS: dict[str, float] = {
    "ludakopeikina@gmail.com": 1.0,
    "vivmuk@gmail.com": 1.0,
}

KEYWORD_WEIGHTS: dict[str, float] = {
    "urgent": 3.0,
    "asap": 3.0,
    "blocker": 3.0,
    "critical": 2.5,
    "deadline": 2.0,
    "important": 1.5,
    "please review": 1.5,
    "action required": 2.0,
    "update": 0.5,
    "fyi": -1.0,
    "no action": -2.0,
}

# Minimum score to create Basecamp items
PRIORITY_THRESHOLD = 3.0


def score_email(email: EmailThread, classified: ClassifiedEmail | None = None) -> float:
    """Score an email for priority based on multiple signals.

    Returns a float score. Emails below PRIORITY_THRESHOLD are filtered out.
    """
    score = 0.0

    # 1. Sender weight (base importance)
    sender_lower = email.sender.lower()
    for addr, weight in SENDER_WEIGHTS.items():
        if addr in sender_lower:
            score += weight * 3  # Base sender score = 3
            break

    # 2. Keyword weight (scan subject + body)
    text = f"{email.subject} {email.body[:500]}".lower()
    for keyword, weight in KEYWORD_WEIGHTS.items():
        if keyword in text:
            score += weight

    # 3. Priority from AI classification
    if classified:
        priority_bonus = {"high": 3.0, "medium": 1.0, "low": -1.0}
        score += priority_bonus.get(classified.priority, 0)

        # Actionable content bonus
        if classified.todos:
            score += min(len(classified.todos), 5) * 0.5

        # Discussion-only penalty
        if classified.type == "discussion" and not classified.todos:
            score -= 2.0

    # 4. Thread length signal (longer threads = more important)
    body_length = len(email.body)
    if body_length > 1000:
        score += 1.0
    elif body_length > 500:
        score += 0.5

    return max(0.0, score)


def should_process(score: float) -> bool:
    """Check if an email should be converted to Basecamp items."""
    return score >= PRIORITY_THRESHOLD
