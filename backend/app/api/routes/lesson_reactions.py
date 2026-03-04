"""Lesson Reactions API routes — toggle reactions on lessons."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_database
from app.models.lesson import Lesson
from app.models.learning_path import LearningPath
from app.models.lesson_reaction import LessonReaction
from app.schemas.lesson_reaction import (
    ToggleReactionRequest,
    LessonReactionStateResponse,
)

router = APIRouter()

VALID_REACTIONS = {"helpful", "interesting", "mind_blown", "confused"}


@router.post(
    "/{path_id}/lessons/{lesson_id}/react",
    response_model=LessonReactionStateResponse,
)
async def toggle_reaction(
    path_id: str,
    lesson_id: str,
    request: ToggleReactionRequest,
    db: AsyncSession = Depends(get_database),
):
    """Toggle a reaction on a lesson (add if absent, remove if present)."""
    # Validate lesson belongs to path
    lesson = await db.get(Lesson, lesson_id)
    if not lesson or lesson.path_id != path_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get user_id from path
    path = await db.get(LearningPath, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    user_id = path.user_id

    # Check if reaction already exists
    result = await db.execute(
        select(LessonReaction).where(
            LessonReaction.user_id == user_id,
            LessonReaction.lesson_id == lesson_id,
            LessonReaction.reaction == request.reaction,
        )
    )
    existing = result.scalars().first()

    if existing:
        # Remove (toggle off)
        await db.delete(existing)
    else:
        # Add (toggle on)
        reaction = LessonReaction(
            user_id=user_id,
            lesson_id=lesson_id,
            reaction=request.reaction,
        )
        db.add(reaction)

    await db.commit()

    # Return current state
    return await _get_reaction_state(db, user_id, lesson_id)


@router.get(
    "/{path_id}/lessons/{lesson_id}/reactions",
    response_model=LessonReactionStateResponse,
)
async def get_reactions(
    path_id: str,
    lesson_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get current reactions for a user on a lesson."""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson or lesson.path_id != path_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    path = await db.get(LearningPath, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    return await _get_reaction_state(db, path.user_id, lesson_id)


async def _get_reaction_state(
    db: AsyncSession, user_id: str, lesson_id: str
) -> LessonReactionStateResponse:
    """Build the reaction state response."""
    result = await db.execute(
        select(LessonReaction).where(
            LessonReaction.user_id == user_id,
            LessonReaction.lesson_id == lesson_id,
        )
    )
    reactions = [r.reaction for r in result.scalars().all()]
    return LessonReactionStateResponse(
        reactions=reactions,
        confusion_detected="confused" in reactions,
    )
