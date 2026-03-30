"""Topic-thread mapping model for Communication Intelligence."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TopicThreadMap(Base):
    """Maps Gmail thread IDs to Basecamp topic/todolist IDs.

    Enforces 1:1 mapping so that replies in the same email thread
    append to the existing Basecamp topic instead of creating duplicates.
    """

    __tablename__ = "topic_thread_maps"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email_thread_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )  # Gmail thread ID
    basecamp_topic_id: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Basecamp message/topic ID
    basecamp_todolist_id: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # Basecamp todolist ID (linked to topic)
    status: Mapped[str] = mapped_column(
        String(50), default="active", nullable=False
    )  # active | resolved | stalled
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
