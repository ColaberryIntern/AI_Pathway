"""Lesson model — content generated on-demand by LessonGeneratorAgent."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Lesson(Base):
    """An individual lesson within a module.

    Content is null until the learner starts the lesson, at which point
    the LessonGeneratorAgent generates it on-demand and caches it here.
    """

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    module_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("modules.id"), nullable=False
    )
    path_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("learning_paths.id"), nullable=False
    )
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    lesson_type: Mapped[str] = mapped_column(
        String(50), default="standard"
    )  # standard, reinforcement, project
    content: Mapped[dict] = mapped_column(
        JSON, nullable=True
    )  # {explanation, code_examples[], exercises[], knowledge_checks[], hands_on_tasks[]}
    status: Mapped[str] = mapped_column(
        String(20), default="not_started"
    )  # not_started, in_progress, completed
    quiz_score: Mapped[float] = mapped_column(Float, nullable=True)
    exercise_attempts: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="lessons")
    learning_path: Mapped["LearningPath"] = relationship(
        "LearningPath", back_populates="lessons"
    )
