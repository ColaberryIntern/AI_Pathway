"""Profile model."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Profile(Base):
    """User profile model (from 12 test profiles or custom)."""

    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, default="custom"
    )  # 'test_profile' or 'custom'
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_role: Mapped[str] = mapped_column(String(255), nullable=False)
    target_role: Mapped[str] = mapped_column(String(255), nullable=True)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=True)
    ai_exposure_level: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # None/Basic/Intermediate/Advanced
    learning_intent: Mapped[str] = mapped_column(Text, nullable=True)
    profile_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # Full profile JSON
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profiles")
