"""Ontology API routes."""
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_ontology
from app.services.ontology import OntologyService

router = APIRouter()


@router.get("/")
async def get_full_ontology(
    ontology: OntologyService = Depends(get_ontology),
):
    """Get the full ontology data."""
    return ontology.get_full_ontology()


@router.get("/skills")
async def list_skills(
    domain: str | None = Query(None, description="Filter by domain ID"),
    level: int | None = Query(None, description="Filter by proficiency level"),
    ontology: OntologyService = Depends(get_ontology),
):
    """List all skills with optional filters."""
    skills = ontology.skills

    if domain:
        skills = [s for s in skills if s["domain"] == domain]

    if level is not None:
        skills = [s for s in skills if s.get("level") == level]

    return {"skills": skills, "total": len(skills)}


@router.get("/skills/{skill_id}")
async def get_skill(
    skill_id: str,
    ontology: OntologyService = Depends(get_ontology),
):
    """Get a skill by ID with its prerequisites."""
    skill = ontology.get_skill(skill_id)

    if not skill:
        return {"error": "Skill not found"}

    prerequisites = ontology.get_skill_prerequisites(skill_id)
    dependents = ontology.get_skill_dependents(skill_id)
    domain = ontology.get_domain(skill["domain"])

    return {
        "skill": skill,
        "domain": domain,
        "prerequisites": prerequisites,
        "dependents": dependents,
    }


@router.get("/skills/{skill_id}/prerequisites")
async def get_skill_prerequisites(
    skill_id: str,
    ontology: OntologyService = Depends(get_ontology),
):
    """Get prerequisite chain for a skill."""
    prerequisites = ontology.get_skill_prerequisites(skill_id)
    return {"skill_id": skill_id, "prerequisites": prerequisites}


@router.get("/domains")
async def list_domains(
    ontology: OntologyService = Depends(get_ontology),
):
    """List all domains."""
    return {"domains": ontology.domains}


@router.get("/domains/{domain_id}")
async def get_domain(
    domain_id: str,
    ontology: OntologyService = Depends(get_ontology),
):
    """Get a domain with its skills."""
    domain = ontology.get_domain(domain_id)

    if not domain:
        return {"error": "Domain not found"}

    skills = ontology.get_skills_by_domain(domain_id)

    return {"domain": domain, "skills": skills}


@router.get("/layers")
async def list_layers(
    ontology: OntologyService = Depends(get_ontology),
):
    """List all layers."""
    return {"layers": ontology.layers}


@router.get("/roles")
async def list_roles(
    ontology: OntologyService = Depends(get_ontology),
):
    """List all roles."""
    return {"roles": ontology.roles}


@router.get("/roles/{role_id}/skills")
async def get_role_skills(
    role_id: str,
    ontology: OntologyService = Depends(get_ontology),
):
    """Get skills relevant to a role."""
    skills = ontology.get_role_skills(role_id)
    return {"role_id": role_id, "skills": skills}


@router.get("/proficiency-scale")
async def get_proficiency_scale(
    ontology: OntologyService = Depends(get_ontology),
):
    """Get the proficiency scale."""
    return {"proficiency_scale": ontology.proficiency_scale}


@router.get("/search")
async def search_skills(
    q: str = Query(..., description="Search query"),
    domain: str | None = Query(None, description="Filter by domain"),
    level: int | None = Query(None, description="Filter by level"),
    ontology: OntologyService = Depends(get_ontology),
):
    """Search skills by name."""
    results = ontology.search_skills(q, domain, level)
    return {"query": q, "results": results, "total": len(results)}
