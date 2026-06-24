"""Contracts for the Enterprise Base Curriculum admin API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class EnterpriseCurriculumUpdate(BaseModel):
    """Request body for setting the global enterprise base curriculum."""

    skill_ids: list[str] = Field(default_factory=list)
    label: str = ""


class EnterpriseCurriculumResponse(BaseModel):
    """Current base curriculum, with ontology-resolved names for display."""

    skill_ids: list[str]
    skills: list[dict]          # [{skill_id, name, domain, level}]
    label: str = ""
    updated_at: str | None = None
