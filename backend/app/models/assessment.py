"""Assessment model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Assessment(Base):
    """Assessment/quiz responses and skill scores model."""

    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    goal_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("goals.id"), nullable=True
    )
    quiz_questions: Mapped[dict] = mapped_column(JSON, nullable=True)
    responses: Mapped[dict] = mapped_column(JSON, nullable=True)
    state_a_skills: Mapped[dict] = mapped_column(JSON, nullable=True)  # Assessed skills
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="assessments")
    goal: Mapped["Goal"] = relationship("Goal", back_populates="assessments")
