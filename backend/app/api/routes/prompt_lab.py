"""Prompt Lab API routes — LLM proxy for interactive prompt execution."""
import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.lesson import Lesson
from app.models.learning_path import LearningPath
from app.models.prompt_history import PromptHistory
from app.services.llm import get_llm_provider
from app.models.module import Module
from app.schemas.prompt_lab import (
    PromptExecutionRequest,
    PromptExecutionResponse,
    PromptHistoryItem,
    PromptHistoryResponse,
    ImplementationTaskSubmitRequest,
    ImplementationTaskFeedbackResponse,
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
    # Validate path and lesson exist
    path = await db.get(LearningPath, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

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
        llm_response = await llm.generate(
            prompt=request.prompt,
            system_prompt=PROMPT_LAB_SYSTEM,
            max_tokens=MAX_RESPONSE_TOKENS,
            temperature=0.7,
        )
        response_text = llm_response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM execution failed: {str(e)}")

    execution_time_ms = int((time.time() - start_time) * 1000)

    user_id = path.user_id

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


TASK_REVIEW_SYSTEM = """You are an expert AI learning coach reviewing a learner's implementation task submission.
The learner completed a hands-on task and is submitting their prompt engineering strategy for feedback.

Evaluate their work and provide:
1. Specific strengths in their approach (2-3 bullet points)
2. Areas for improvement (2-3 bullet points)
3. A brief overall feedback paragraph (2-3 sentences)

Be encouraging but honest. Focus on prompt engineering technique, not just correctness.
Keep total response under 500 words."""


@router.post(
    "/{path_id}/implementation-task/submit",
    response_model=ImplementationTaskFeedbackResponse,
)
async def submit_implementation_task(
    path_id: str,
    request: ImplementationTaskSubmitRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit an implementation task and get AI feedback on the learner's strategy."""
    path = await db.get(LearningPath, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    lesson = await db.get(Lesson, request.lesson_id)
    if not lesson or lesson.path_id != path_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Build context from lesson content
    content = lesson.content or {}
    task_info = content.get("implementation_task", {})
    module = await db.get(Module, lesson.module_id)

    prompt = f"""TASK: {task_info.get('title', lesson.title)}
DESCRIPTION: {task_info.get('description', '')}
SKILL: {module.skill_name if module else 'Unknown'}

LEARNER'S PROMPT HISTORY:
{request.prompt_history_summary or '(No prompt history provided)'}

LEARNER'S STRATEGY EXPLANATION:
{request.strategy_explanation}

Please evaluate their implementation approach and prompt engineering strategy."""

    llm = get_llm_provider()
    try:
        llm_response = await llm.generate(
            prompt=prompt,
            system_prompt=TASK_REVIEW_SYSTEM,
            max_tokens=1024,
            temperature=0.5,
        )
        feedback_text = llm_response.content
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Feedback generation failed: {str(e)}"
        )

    # Parse strengths and improvements from the response
    strengths = []
    improvements = []
    current_section = None
    for line in feedback_text.split("\n"):
        stripped = line.strip()
        lower = stripped.lower()
        if "strength" in lower or "well" in lower and ":" in lower:
            current_section = "strengths"
            continue
        elif "improve" in lower or "consider" in lower and ":" in lower:
            current_section = "improvements"
            continue
        elif stripped.startswith(("- ", "* ", "1.", "2.", "3.")):
            item = stripped.lstrip("-*0123456789. ").strip()
            if item:
                if current_section == "strengths" and len(strengths) < 3:
                    strengths.append(item)
                elif current_section == "improvements" and len(improvements) < 3:
                    improvements.append(item)

    return ImplementationTaskFeedbackResponse(
        feedback=feedback_text,
        strengths=strengths,
        improvements=improvements,
    )
