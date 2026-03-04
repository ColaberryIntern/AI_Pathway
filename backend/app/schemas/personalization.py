"""Pydantic schemas for Personalization service."""
from typing import Literal
from pydantic import BaseModel


class StrugglingSkill(BaseModel):
    skill_name: str
    signal: str  # e.g. "low quiz scores", "confusion detected"


class StrongSkill(BaseModel):
    skill_name: str
    mastery: float


class SuggestedReview(BaseModel):
    lesson_id: str
    title: str
    reason: str


class NextFocus(BaseModel):
    skill_name: str
    reason: str


class PersonalizationResult(BaseModel):
    struggling_skills: list[StrugglingSkill]
    strong_skills: list[StrongSkill]
    suggested_review: list[SuggestedReview]
    pace_recommendation: Literal["slow_down", "on_track", "can_accelerate"]
    next_focus: NextFocus | None = None
