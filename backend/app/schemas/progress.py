"""Progress schemas."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class ProgressCreate(BaseModel):
    """Schema for creating progress tracking."""

    path_id: str


class ProgressUpdate(BaseModel):
    """Schema for updating progress."""

    chapter: int
    status: Literal["not_started", "in_progress", "completed"]
    quiz_score: float | None = None


class ProgressResponse(BaseModel):
    """Schema for progress response."""

    id: str
    user_id: str
    path_id: str
    current_chapter: int
    chapter_status: dict | None
    quiz_scores: dict | None
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    """Schema for user dashboard."""

    user_id: str
    active_paths: list[dict]
    completed_paths: list[dict]
    total_skills_learned: int
    total_paths: int
