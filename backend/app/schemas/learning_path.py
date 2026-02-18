"""Learning path schemas."""
from datetime import datetime
from pydantic import BaseModel


class Exercise(BaseModel):
    """Schema for a chapter exercise."""

    id: str
    title: str
    description: str
    type: str  # "hands-on", "quiz", "project", "reflection"
    estimated_time_minutes: int | None = None
    instructions: list[str] | None = None
    deliverable: str | None = None


class Resource(BaseModel):
    """Schema for a learning resource."""

    title: str
    url: str | None = None
    type: str  # "article", "video", "tutorial", "documentation", "course"
    source: str | None = None
    description: str | None = None


class ChapterContent(BaseModel):
    """Schema for chapter content."""

    chapter_number: int
    skill_id: str
    skill_name: str
    title: str
    learning_objectives: list[str]
    current_level: int
    target_level: int
    core_concepts: list[dict]  # [{title, content, examples}]
    exercises: list[Exercise]
    self_assessment_questions: list[dict]  # [{question, options, answer}]
    resources: list[Resource] | None = None
    industry_context: str | None = None
    estimated_time_hours: float | None = None


class LearningPathCreate(BaseModel):
    """Schema for creating a learning path."""

    goal_id: str
    gap_id: str
    top_skills: int = 5  # Number of skills to include


class LearningPathResponse(BaseModel):
    """Schema for learning path response."""

    id: str
    user_id: str
    goal_id: str
    gap_id: str
    title: str | None
    description: str | None
    chapters: list[ChapterContent] | None
    total_chapters: int
    created_at: datetime

    class Config:
        from_attributes = True
