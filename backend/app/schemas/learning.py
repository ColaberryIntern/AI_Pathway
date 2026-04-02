"""Learning execution schemas — modules, lessons, skill mastery, dashboard."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


# ── Lesson Outline (part of module) ──────────────────────────────────

class LessonOutline(BaseModel):
    """Lesson outline within a module (no full content yet)."""

    id: str | None = None  # lesson DB id, populated at dashboard time
    lesson_number: int
    title: str
    type: Literal["concept", "practice", "assessment"]
    focus_area: str
    estimated_minutes: int


# ── Module ───────────────────────────────────────────────────────────

class ModuleResponse(BaseModel):
    """Module response with lesson outlines and progress."""

    id: str
    chapter_number: int
    skill_id: str
    skill_name: str
    title: str
    current_level: int
    target_level: int
    lesson_outline: list[LessonOutline] | None
    total_lessons: int
    completed_lessons: int = 0
    status: Literal["not_started", "in_progress", "completed"] = "not_started"

    class Config:
        from_attributes = True


# ── Lesson ───────────────────────────────────────────────────────────

class LessonResponse(BaseModel):
    """Full lesson response including generated content."""

    id: str
    module_id: str
    lesson_number: int
    title: str
    lesson_type: str
    content: dict | None  # null until generated on-demand
    status: Literal["not_started", "in_progress", "completed"]
    quiz_score: float | None
    exercise_attempts: int = 0

    class Config:
        from_attributes = True


class LessonCompleteRequest(BaseModel):
    """Request body for marking a lesson as complete."""

    quiz_score: float | None = None
    exercise_completed: bool = False


class LessonCompleteResponse(BaseModel):
    """Response after completing a lesson."""

    lesson: LessonResponse
    module_progress: ModuleResponse
    skill_mastery_update: "SkillMasteryResponse | None" = None


# ── Skill Mastery ────────────────────────────────────────────────────

class SkillMasteryResponse(BaseModel):
    """Skill mastery progress for a single skill."""

    skill_id: str
    skill_name: str
    initial_level: int
    current_level: float
    target_level: int
    lessons_completed: int
    total_lessons: int
    avg_quiz_score: float | None
    progress_percentage: float = 0.0

    class Config:
        from_attributes = True


# ── Activation ───────────────────────────────────────────────────────

class ActivatePathResponse(BaseModel):
    """Response after activating a learning path."""

    modules: list[ModuleResponse]
    total_lessons: int
    skill_masteries: list[SkillMasteryResponse]


# ── Dashboard ────────────────────────────────────────────────────────

class LearningDashboardResponse(BaseModel):
    """Full learning dashboard data for a single path."""

    path_id: str
    path_title: str
    target_role: str
    overall_progress: float  # 0-100
    modules: list[ModuleResponse]
    skill_masteries: list[SkillMasteryResponse]
    current_module: ModuleResponse | None
    next_lesson: LessonOutline | None
    next_lesson_id: str | None = None
    total_lessons_completed: int
    total_lessons: int
    estimated_hours_remaining: float
