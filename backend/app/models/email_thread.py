"""Email thread model for Communication Intelligence."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class EmailThread(Base):
    """Ingested email messages from Gmail."""

    __tablename__ = "email_threads"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    thread_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )  # Gmail thread ID
    message_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )  # Gmail message ID (dedup key)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    recipients: Mapped[list] = mapped_column(JSON, nullable=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    processed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    skipped: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # Skipped by priority filter
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    classified_data: Mapped[dict] = mapped_column(
        JSON, nullable=True
    )  # AI classification output
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
