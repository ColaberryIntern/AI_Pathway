"""Lesson Reaction model — lightweight per-lesson feedback signals."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class LessonReaction(Base):
    """A single reaction from a user on a lesson.

    Supported reactions: helpful, interesting, mind_blown, confused.
    Each (user, lesson, reaction) triple is unique — toggling is handled at the API layer.
    """

    __tablename__ = "lesson_reactions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lessons.id"), nullable=False
    )
    reaction: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # helpful | interesting | mind_blown | confused
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", "reaction", name="uq_user_lesson_reaction"),
    )
