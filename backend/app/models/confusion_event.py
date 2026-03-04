"""Confusion Event model — tracks confusion signals and recovery attempts."""
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ConfusionEvent(Base):
    """Records when a learner signals confusion and the recovery content generated."""

    __tablename__ = "confusion_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lessons.id"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(String(100), nullable=True)
    section: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # which section confused them
    recovery_content: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
