"""Goal schemas."""
from datetime import datetime
from pydantic import BaseModel


class GoalCreate(BaseModel):
    """Schema for creating a goal."""

    profile_id: str | None = None
    target_role: str
    target_jd_text: str | None = None
    learning_intent: str | None = None


class GoalResponse(BaseModel):
    """Schema for goal response."""

    id: str
    user_id: str
    profile_id: str | None
    target_role: str
    target_jd_text: str | None
    learning_intent: str | None
    state_b_skills: dict | None
    created_at: datetime

    class Config:
        from_attributes = True
