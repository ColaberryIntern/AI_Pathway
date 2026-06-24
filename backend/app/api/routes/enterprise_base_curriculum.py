"""Enterprise Base Curriculum admin API (MVP).

GET  /api/admin/enterprise-base-curriculum/   -> current base skills (+ names)
PUT  /api/admin/enterprise-base-curriculum/   -> set the base skills

Contract enforcement (CLAUDE.md): every skill_id in a PUT is validated against
the ontology at the boundary. Unknown ids are rejected with 422 - we do not
silently drop them, because a typo'd base curriculum would quietly teach the
wrong foundation to every learner.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_ontology
from app.schemas.enterprise_base_curriculum import (
    EnterpriseCurriculumResponse,
    EnterpriseCurriculumUpdate,
)
from app.services.enterprise_base_curriculum import get_base_curriculum_service
from app.services.ontology import OntologyService

router = APIRouter()


def _resolve_skills(skill_ids: list[str], ontology: OntologyService) -> list[dict]:
    out: list[dict] = []
    for sid in skill_ids:
        sk = ontology.get_skill(sid) or {}
        out.append({
            "skill_id": sid,
            "name": sk.get("name", sid),
            "domain": sk.get("domain", ""),
            "level": sk.get("level"),
        })
    return out


@router.get("/", response_model=EnterpriseCurriculumResponse)
async def get_enterprise_base_curriculum(
    ontology: OntologyService = Depends(get_ontology),
):
    """Return the current global base curriculum with display names."""
    data = get_base_curriculum_service().get()
    return EnterpriseCurriculumResponse(
        skill_ids=data["skill_ids"],
        skills=_resolve_skills(data["skill_ids"], ontology),
        label=data.get("label", ""),
        updated_at=data.get("updated_at"),
    )


@router.put("/", response_model=EnterpriseCurriculumResponse)
async def update_enterprise_base_curriculum(
    body: EnterpriseCurriculumUpdate,
    ontology: OntologyService = Depends(get_ontology),
):
    """Set the global base curriculum. Validates every skill_id against the
    ontology; rejects the whole request if any id is unknown."""
    valid = ontology.get_all_skill_ids()
    unknown = [sid for sid in body.skill_ids if sid not in valid]
    if unknown:
        raise HTTPException(
            status_code=422,
            detail={"error": "unknown skill_ids", "unknown": unknown},
        )
    now = datetime.now(timezone.utc).isoformat()
    saved = get_base_curriculum_service().update(body.skill_ids, body.label, now)
    return EnterpriseCurriculumResponse(
        skill_ids=saved["skill_ids"],
        skills=_resolve_skills(saved["skill_ids"], ontology),
        label=saved.get("label", ""),
        updated_at=saved.get("updated_at"),
    )
