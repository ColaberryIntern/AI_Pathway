"""Progress model."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Progress(Base):
    """Chapter completion and progress tracking model."""

    __tablename__ = "progress"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    path_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("learning_paths.id"), nullable=False
    )
    current_chapter: Mapped[int] = mapped_column(Integer, default=1)
    chapter_status: Mapped[dict] = mapped_column(
        JSON, nullable=True
    )  # {1: "completed", 2: "in_progress", ...}
    quiz_scores: Mapped[dict] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="progress_records")
    learning_path: Mapped["LearningPath"] = relationship(
        "LearningPath", back_populates="progress_records"
    )
