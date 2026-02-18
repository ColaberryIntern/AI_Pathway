"""Profile schemas."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class ProfileCreate(BaseModel):
    """Schema for creating a profile."""

    name: str
    current_role: str
    target_role: str | None = None
    industry: str
    experience_years: int | None = None
    ai_exposure_level: Literal["None", "Basic", "Intermediate", "Advanced"] | None = None
    learning_intent: str | None = None
    profile_data: dict | None = None


class ProfileUpload(BaseModel):
    """Schema for uploading a custom profile."""

    name: str
    current_role: str
    target_role: str | None = None
    industry: str
    experience_years: int | None = None
    ai_exposure_level: Literal["None", "Basic", "Intermediate", "Advanced"] | None = None
    learning_intent: str | None = None
    current_skills: dict | None = None  # Current skill levels
    target_jd: str | None = None  # Target job description


class ProfileResponse(BaseModel):
    """Schema for profile response."""

    id: str
    user_id: str | None
    source: str
    name: str
    current_role: str
    target_role: str | None
    industry: str
    experience_years: int | None
    ai_exposure_level: str | None
    learning_intent: str | None
    profile_data: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileSummary(BaseModel):
    """Schema for profile list summary."""

    id: str
    name: str
    current_role: str
    target_role: str | None
    industry: str

    class Config:
        from_attributes = True
