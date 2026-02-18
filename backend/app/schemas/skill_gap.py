"""Skill gap schemas."""
from datetime import datetime
from pydantic import BaseModel


class SkillGapItem(BaseModel):
    """Schema for a single skill gap."""

    skill_id: str
    skill_name: str
    domain: str
    current_level: int
    target_level: int
    gap: int
    priority: int  # 1 = highest priority
    priority_reason: str | None = None
    prerequisites: list[str] | None = None


class SkillGapCreate(BaseModel):
    """Schema for creating skill gap analysis."""

    goal_id: str
    assessment_id: str | None = None
    state_a_skills: dict | None = None
    state_b_skills: dict | None = None


class SkillGapResponse(BaseModel):
    """Schema for skill gap response."""

    id: str
    user_id: str
    goal_id: str
    assessment_id: str | None
    state_a_skills: dict | None
    state_b_skills: dict | None
    gaps: list[SkillGapItem] | None
    created_at: datetime

    class Config:
        from_attributes = True
