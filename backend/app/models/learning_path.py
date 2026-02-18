"""Learning path model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class LearningPath(Base):
    """Generated 5-chapter learning path model."""

    __tablename__ = "learning_paths"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    goal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("goals.id"), nullable=False
    )
    gap_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("skill_gaps.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    chapters: Mapped[dict] = mapped_column(JSON, nullable=True)  # 5 chapters
    total_chapters: Mapped[int] = mapped_column(default=5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_paths")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="learning_paths")
    skill_gap: Mapped["SkillGap"] = relationship("SkillGap", back_populates="learning_paths")
    progress_records: Mapped[list["Progress"]] = relationship(
        "Progress", back_populates="learning_path", cascade="all, delete-orphan"
    )
