"""Confusion Recovery API routes — generate alternative explanations."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_database, get_llm, get_rag
from app.models.lesson import Lesson
from app.models.learning_path import LearningPath
from app.services.llm.base import BaseLLMProvider
from app.services.rag.retriever import RAGRetriever
from app.services.confusion_recovery import ConfusionRecoveryService
from app.schemas.confusion_recovery import (
    ConfusionRecoveryRequest,
    ConfusionRecoveryResponse,
)

router = APIRouter()
recovery_svc = ConfusionRecoveryService()


@router.post(
    "/{path_id}/lessons/{lesson_id}/confusion-recovery",
    response_model=ConfusionRecoveryResponse,
)
async def generate_confusion_recovery(
    path_id: str,
    lesson_id: str,
    request: ConfusionRecoveryRequest,
    db: AsyncSession = Depends(get_database),
    llm: BaseLLMProvider = Depends(get_llm),
    rag: RAGRetriever = Depends(get_rag),
):
    """Generate alternative explanation for a confused learner."""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson or lesson.path_id != path_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    path = await db.get(LearningPath, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    recovery = await recovery_svc.generate_recovery(
        db=db,
        llm=llm,
        rag=rag,
        lesson=lesson,
        section=request.section,
        user_id=path.user_id,
    )

    await db.commit()

    return ConfusionRecoveryResponse(**recovery)
