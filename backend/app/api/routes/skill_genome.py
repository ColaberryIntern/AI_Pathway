"""Skill Genome API routes — global per-user mastery overlay."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_database
from app.services.skill_genome import SkillGenomeService
from app.schemas.skill_genome import SkillGenomeEntryResponse, SkillGenomeResponse

router = APIRouter()
genome_svc = SkillGenomeService()


@router.get("/{user_id}", response_model=SkillGenomeResponse)
async def get_skill_genome(
    user_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get the full Skill Genome for a user."""
    entries = await genome_svc.get_genome(db, user_id)
    return SkillGenomeResponse(
        user_id=user_id,
        entries=[
            SkillGenomeEntryResponse(
                ontology_node_id=e.ontology_node_id,
                skill_name=e.skill_name,
                domain=e.domain,
                mastery_level=round(e.mastery_level, 2),
                evidence_count=e.evidence_count,
                last_evidence=e.last_evidence,
                confidence=round(e.confidence, 2),
                updated_at=e.updated_at.isoformat(),
            )
            for e in entries
        ],
        total_skills=len(entries),
    )


@router.get("/{user_id}/{skill_id}", response_model=SkillGenomeEntryResponse)
async def get_skill_genome_entry(
    user_id: str,
    skill_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get a single Skill Genome entry."""
    entry = await genome_svc.get_skill_entry(db, user_id, skill_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Skill genome entry not found")

    return SkillGenomeEntryResponse(
        ontology_node_id=entry.ontology_node_id,
        skill_name=entry.skill_name,
        domain=entry.domain,
        mastery_level=round(entry.mastery_level, 2),
        evidence_count=entry.evidence_count,
        last_evidence=entry.last_evidence,
        confidence=round(entry.confidence, 2),
        updated_at=entry.updated_at.isoformat(),
    )
