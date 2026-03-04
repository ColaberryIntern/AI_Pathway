"""Skill mastery model — tracks per-skill progress across the learning journey."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SkillMastery(Base):
    """Tracks a learner's mastery progress for a single skill within a learning path.

    current_level is a float to represent fractional progress
    (e.g., started at 1, target 3, completed 2 of 4 lessons → current_level = 2.0).
    """

    __tablename__ = "skill_mastery"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    path_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("learning_paths.id"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(String(50), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    initial_level: Mapped[int] = mapped_column(Integer, default=0)
    current_level: Mapped[float] = mapped_column(Float, default=0.0)
    target_level: Mapped[int] = mapped_column(Integer, default=1)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_lessons: Mapped[int] = mapped_column(Integer, default=0)
    avg_quiz_score: Mapped[float] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="skill_masteries")
    learning_path: Mapped["LearningPath"] = relationship(
        "LearningPath", back_populates="skill_masteries"
    )
