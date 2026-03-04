"""Skill Genome model — tracks global per-user skill mastery across all paths."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SkillGenomeEntry(Base):
    """Global mastery overlay on the ontology — one entry per (user, skill).

    Unlike SkillMastery (which is per-path), SkillGenome aggregates evidence
    across all learning paths to give a single mastery view per skill.
    """

    __tablename__ = "skill_genome"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    ontology_node_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=True)
    mastery_level: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    last_evidence: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # "quiz" | "lesson" | "project" | "mentor"
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "ontology_node_id", name="uq_genome_user_skill"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
