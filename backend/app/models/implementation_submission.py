"""Implementation Submission model — tracks artifact submissions and AI grading."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ImplementationSubmission(Base):
    """Records each implementation task submission for grading.

    Supports multiple attempts per lesson (resubmission).
    Stores artifact text, file metadata, extracted content, and AI grading results.
    """

    __tablename__ = "implementation_submissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    lesson_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("lessons.id"), nullable=False
    )
    path_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("learning_paths.id"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    artifact_text: Mapped[str] = mapped_column(Text, default="")
    file_names: Mapped[list] = mapped_column(JSON, default=list)
    extracted_content: Mapped[str] = mapped_column(Text, default="")
    score: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback: Mapped[str] = mapped_column(Text, default="")
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    improvements: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
