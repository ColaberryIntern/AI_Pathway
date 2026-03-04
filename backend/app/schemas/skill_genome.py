"""Pydantic schemas for Skill Genome endpoints."""
from pydantic import BaseModel


class SkillGenomeEntryResponse(BaseModel):
    """Single skill genome entry."""
    ontology_node_id: str
    skill_name: str
    domain: str | None = None
    mastery_level: float
    evidence_count: int
    last_evidence: str | None = None
    confidence: float
    updated_at: str


class SkillGenomeResponse(BaseModel):
    """Full genome for a user."""
    user_id: str
    entries: list[SkillGenomeEntryResponse]
    total_skills: int
