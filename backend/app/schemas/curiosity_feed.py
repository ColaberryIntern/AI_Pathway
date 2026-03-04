"""Pydantic schemas for Curiosity Feed."""
from pydantic import BaseModel


class CuriosityFeedItem(BaseModel):
    skill_id: str
    skill_name: str
    domain: str | None = None
    domain_label: str | None = None
    teaser: str
    unlocked_by: str  # which completed skill unlocked this
    relevance_score: float
    has_learning_path: bool = False


class CuriosityFeedResponse(BaseModel):
    user_id: str
    items: list[CuriosityFeedItem]
    total_items: int
