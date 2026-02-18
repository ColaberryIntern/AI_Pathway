"""Agent log model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AgentLog(Base):
    """Agent execution logs for debugging and improvement."""

    __tablename__ = "agent_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    error: Mapped[str] = mapped_column(String(1000), nullable=True)
    duration_ms: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
