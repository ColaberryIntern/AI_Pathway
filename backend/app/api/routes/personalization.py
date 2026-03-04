"""Personalization API routes — adaptive recommendations."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_database
from app.services.personalization import PersonalizationService
from app.schemas.personalization import PersonalizationResult

router = APIRouter()
personalization_svc = PersonalizationService()


@router.get("/{user_id}", response_model=PersonalizationResult)
async def get_personalization(
    user_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get personalized learning recommendations for a user."""
    result = await personalization_svc.get_recommendations(db, user_id)
    return PersonalizationResult(**result)


@router.get("/{user_id}/path/{path_id}", response_model=PersonalizationResult)
async def get_path_personalization(
    user_id: str,
    path_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get personalized recommendations scoped to a specific learning path."""
    result = await personalization_svc.get_recommendations(db, user_id, path_id)
    return PersonalizationResult(**result)
