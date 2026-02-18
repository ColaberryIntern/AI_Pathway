"""Skill gap model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SkillGap(Base):
    """Calculated skill gaps with priorities model."""

    __tablename__ = "skill_gaps"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    goal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("goals.id"), nullable=False
    )
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id"), nullable=True
    )
    state_a_skills: Mapped[dict] = mapped_column(JSON, nullable=True)
    state_b_skills: Mapped[dict] = mapped_column(JSON, nullable=True)
    gaps: Mapped[dict] = mapped_column(JSON, nullable=True)  # Prioritized gap list
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="skill_gaps")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="skill_gaps")
    learning_paths: Mapped[list["LearningPath"]] = relationship(
        "LearningPath", back_populates="skill_gap", cascade="all, delete-orphan"
    )
