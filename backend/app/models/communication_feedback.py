"""Communication feedback model for execution tracking."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CommunicationFeedback(Base):
    """Tracks execution feedback for email-to-Basecamp pipeline.

    Monitors todo completion rates, recurring topics, and stalled execution
    to surface bottlenecks and insights.
    """

    __tablename__ = "communication_feedback"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    topic_thread_map_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topic_thread_maps.id"), nullable=False
    )
    todos_created: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    todos_completed: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    is_recurring: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    recurrence_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
