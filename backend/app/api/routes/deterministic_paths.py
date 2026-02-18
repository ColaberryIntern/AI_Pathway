"""Deterministic learning-path API routes — Phase 3.2

Exposes the LearningPathGenerator (no LLM, no database) as a
stateless POST endpoint.  Useful for quick previews and testing
before committing a path to the database.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.path_generator import LearningPathGenerator

router = APIRouter()


class PathRequest(BaseModel):
    """Request body for deterministic path generation.

    Attributes
    ----------
    state_a : dict[str, int]
        Learner's current profile — ``{skill_id: current_level}``.
    state_b : dict[str, int]
        Target/required profile — ``{skill_id: required_level}``.
    """

    state_a: dict[str, int]
    state_b: dict[str, int]


@router.post("/generate")
def generate_path(payload: PathRequest):
    """Generate a deterministic, prerequisite-ordered learning path.

    Returns up to 5 chapters, each advancing the learner exactly
    one proficiency level.  No LLM calls, no database writes.
    """
    generator = LearningPathGenerator()

    try:
        result = generator.generate_path(payload.state_a, payload.state_b)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return result
