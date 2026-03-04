"""Mentor Conversation model — stores AI mentor chat history."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MentorConversation(Base):
    """Stores conversation history between a learner and the AI mentor.

    Messages are stored as a JSON array of {role, content, timestamp} dicts.
    One conversation per lesson per user (or a general conversation per path).
    """

    __tablename__ = "mentor_conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    path_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("learning_paths.id"), nullable=False
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lessons.id"), nullable=True
    )
    messages: Mapped[list] = mapped_column(
        JSON, default=list
    )  # [{role: "user"|"mentor", content: str, timestamp: str}]
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
