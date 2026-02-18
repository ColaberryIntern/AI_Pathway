"""Goal model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Goal(Base):
    """Target role and job description model."""

    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("profiles.id"), nullable=True
    )
    target_role: Mapped[str] = mapped_column(String(255), nullable=False)
    target_jd_text: Mapped[str] = mapped_column(Text, nullable=True)
    learning_intent: Mapped[str] = mapped_column(Text, nullable=True)
    state_b_skills: Mapped[dict] = mapped_column(JSON, nullable=True)  # Extracted skills
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="goals")
    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment", back_populates="goal", cascade="all, delete-orphan"
    )
    skill_gaps: Mapped[list["SkillGap"]] = relationship(
        "SkillGap", back_populates="goal", cascade="all, delete-orphan"
    )
    learning_paths: Mapped[list["LearningPath"]] = relationship(
        "LearningPath", back_populates="goal", cascade="all, delete-orphan"
    )
