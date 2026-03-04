"""Prompt Lab API routes — LLM proxy for interactive prompt execution."""
import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.lesson import Lesson
from app.models.prompt_history import PromptHistory
from app.services.llm import get_llm_provider
from app.schemas.prompt_lab import (
    PromptExecutionRequest,
    PromptExecutionResponse,
    PromptHistoryItem,
    PromptHistoryResponse,
)

router = APIRouter()

# Safety system prompt wrapping learner prompts
PROMPT_LAB_SYSTEM = """You are an AI assistant helping a learner practice prompt engineering.
The learner is working on a lesson and experimenting with prompts.
Provide helpful, educational responses that demonstrate good AI output.
Keep responses focused and under 1500 words.
Do not generate harmful, offensive, or inappropriate content.
If the prompt is unclear, explain what information would help you give a better response."""

MAX_ITERATIONS_PER_LESSON = 10
MAX_RESPONSE_TOKENS = 2048


@router.post("/{path_id}/prompt-lab/execute", response_model=PromptExecutionResponse)
async def execute_prompt(
    path_id: str,
    request: PromptExecutionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a learner's prompt against the LLM and return the result.

    Tracks prompt history for the lesson. Rate limited to MAX_ITERATIONS_PER_LESSON.
    """
    # Validate lesson exists and belongs to path
    lesson = await db.get(Lesson, request.lesson_id)
    if not lesson or lesson.path_id != path_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check iteration limit
    count_result = await db.execute(
        select(func.count(PromptHistory.id)).where(
            PromptHistory.lesson_id == request.lesson_id
        )
    )
    current_count = count_result.scalar() or 0
    if current_count >= MAX_ITERATIONS_PER_LESSON:
        raise HTTPException(
            status_code=429,
            detail=f"Maximum {MAX_ITERATIONS_PER_LESSON} prompt iterations per lesson reached",
        )

    # Execute prompt via LLM
    llm = get_llm_provider()
    start_time = time.time()

    try:
        response_text = await llm.generate(
            prompt=request.prompt,
            system_prompt=PROMPT_LAB_SYSTEM,
            max_tokens=MAX_RESPONSE_TOKENS,
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM execution failed: {str(e)}")

    execution_time_ms = int((time.time() - start_time) * 1000)

    # Determine user_id from the lesson's path
    # For now use a placeholder — will be replaced with auth
    user_id = "default_user"

    # Save to prompt history
    iteration = current_count + 1
    history_record = PromptHistory(
        lesson_id=request.lesson_id,
        user_id=user_id,
        iteration=iteration,
        prompt_text=request.prompt,
        response_text=response_text,
        execution_time_ms=execution_time_ms,
    )
    db.add(history_record)
    await db.commit()

    return PromptExecutionResponse(
        response=response_text,
        iteration=iteration,
        tokens_used=0,  # TODO: get from LLM provider when available
        execution_time_ms=execution_time_ms,
    )


@router.get("/{path_id}/prompt-lab/{lesson_id}/history", response_model=PromptHistoryResponse)
async def get_prompt_history(
    path_id: str,
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get prompt iteration history for a lesson."""
    lesson = await db.get(Lesson, lesson_id)
    if not lesson or lesson.path_id != path_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    result = await db.execute(
        select(PromptHistory)
        .where(PromptHistory.lesson_id == lesson_id)
        .order_by(PromptHistory.iteration)
    )
    records = result.scalars().all()

    iterations = [
        PromptHistoryItem(
            iteration=r.iteration,
            prompt_text=r.prompt_text,
            response_text=r.response_text,
            execution_time_ms=r.execution_time_ms,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]

    return PromptHistoryResponse(
        lesson_id=lesson_id,
        iterations=iterations,
        total_iterations=len(iterations),
    )
