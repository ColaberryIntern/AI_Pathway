"""User model."""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    profiles: Mapped[list["Profile"]] = relationship(
        "Profile", back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goal"]] = relationship(
        "Goal", back_populates="user", cascade="all, delete-orphan"
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment", back_populates="user", cascade="all, delete-orphan"
    )
    skill_gaps: Mapped[list["SkillGap"]] = relationship(
        "SkillGap", back_populates="user", cascade="all, delete-orphan"
    )
    learning_paths: Mapped[list["LearningPath"]] = relationship(
        "LearningPath", back_populates="user", cascade="all, delete-orphan"
    )
    progress_records: Mapped[list["Progress"]] = relationship(
        "Progress", back_populates="user", cascade="all, delete-orphan"
    )
