"""Assessment schemas."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class QuizQuestion(BaseModel):
    """Schema for a quiz question."""

    id: str
    skill_id: str
    skill_name: str
    question: str
    question_type: Literal["multiple_choice", "scenario", "self_assessment"]
    options: list[dict] | None = None  # For multiple choice
    correct_answer: str | None = None


class QuizResponse(BaseModel):
    """Schema for quiz response submission."""

    question_id: str
    answer: str
    confidence: int | None = None  # 1-5 scale


class AssessmentCreate(BaseModel):
    """Schema for creating an assessment."""

    goal_id: str | None = None
    skill_ids: list[str] | None = None  # Specific skills to assess


class AssessmentResponse(BaseModel):
    """Schema for assessment response."""

    id: str
    user_id: str
    goal_id: str | None
    quiz_questions: list[QuizQuestion] | None
    responses: list[QuizResponse] | None
    state_a_skills: dict | None
    completed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentSubmit(BaseModel):
    """Schema for submitting assessment responses."""

    assessment_id: str
    responses: list[QuizResponse]
