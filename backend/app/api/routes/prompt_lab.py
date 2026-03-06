"""Prompt Lab API routes — LLM proxy for interactive prompt execution."""
import json
import logging
import time
from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.lesson import Lesson
from app.models.learning_path import LearningPath
from app.models.prompt_history import PromptHistory
from app.models.implementation_submission import ImplementationSubmission
from app.services.llm import get_llm_provider
from app.services.resume_parser import extract_text
from app.models.module import Module
from app.services.skill_genome import SkillGenomeService
from app.schemas.prompt_lab import (
    PromptExecutionRequest,
    PromptExecutionResponse,
    PromptHistoryItem,
    PromptHistoryResponse,
    ImplementationTaskGradeResponse,
)

logger = logging.getLogger(__name__)

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


TASK_GRADING_SYSTEM = """You are an expert AI learning assessor grading a learner's implementation task submission.

The learner was given a specific task with requirements. They are submitting their work artifacts
(text, code, documents, screenshots) for grading.

You must evaluate their submission against the task requirements and return a JSON object with:

{
  "score": <integer 0-100>,
  "passed": <boolean, true if score >= 70>,
  "feedback": "<2-3 sentence overall assessment>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"]
}

Grading criteria:
- Does the submission address ALL stated requirements? (40 points)
- Quality and completeness of the deliverable (30 points)
- Evidence of understanding (not just copy-paste) (20 points)
- Presentation and clarity (10 points)

Be encouraging but rigorous. A score of 70+ means the learner demonstrated adequate understanding.
If the submission is empty or clearly unrelated, score 0-20.
If it partially addresses requirements, score 40-69.
If it fully addresses requirements with good quality, score 70-90.
Reserve 90+ for exceptional work that goes beyond requirements.

Return ONLY the JSON object. No additional text."""

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB per file
MAX_CONTENT_LENGTH = 12_000  # chars sent to LLM
PASS_THRESHOLD = 70
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml",
    ".md", ".txt", ".html", ".css", ".csv", ".xml", ".sql",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
}


@router.post(
    "/{path_id}/implementation-task/submit",
    response_model=ImplementationTaskGradeResponse,
)
async def submit_implementation_task(
    path_id: str,
    lesson_id: str = Form(...),
    artifact_text: str = Form(""),
    files: list[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
):
    """Submit implementation task artifacts for AI grading.

    Accepts text and/or file uploads. Extracts text from files,
    grades against task requirements, and returns structured feedback.
    """
    # Validate path and lesson
    path = await db.get(LearningPath, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    lesson = await db.get(Lesson, lesson_id)
    if not lesson or lesson.path_id != path_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Count previous attempts
    count_result = await db.execute(
        select(func.count(ImplementationSubmission.id)).where(
            ImplementationSubmission.lesson_id == lesson_id,
            ImplementationSubmission.path_id == path_id,
        )
    )
    attempt_number = (count_result.scalar() or 0) + 1

    # Extract text from uploaded files
    file_names: list[str] = []
    extracted_parts: list[str] = []

    for f in files:
        if not f.filename:
            continue
        ext = "." + f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Allowed: PDF, DOCX, code files, images.",
            )
        contents = await f.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File {f.filename} exceeds 10MB limit.",
            )
        file_names.append(f.filename)
        try:
            text = extract_text(contents, f.filename)
            if text.strip():
                extracted_parts.append(f"--- {f.filename} ---\n{text}")
        except Exception as e:
            logger.warning("Failed to extract text from %s: %s", f.filename, e)
            extracted_parts.append(f"--- {f.filename} ---\n[Could not extract text]")

    # Combine all content
    all_extracted = "\n\n".join(extracted_parts)
    combined_content = ""
    if artifact_text.strip():
        combined_content += f"PASTED TEXT:\n{artifact_text.strip()}\n\n"
    if all_extracted:
        combined_content += f"UPLOADED FILES:\n{all_extracted}"

    if not combined_content.strip():
        raise HTTPException(
            status_code=400,
            detail="No content submitted. Please paste text or upload files.",
        )

    # Truncate to stay within LLM context limits
    combined_content = combined_content[:MAX_CONTENT_LENGTH]

    # Build grading prompt from task info
    content = lesson.content or {}
    task_info = content.get("implementation_task", {})
    module = await db.get(Module, lesson.module_id)

    requirements = task_info.get("requirements", [])
    req_list = "\n".join(f"{i+1}. {r}" for i, r in enumerate(requirements))

    grading_prompt = f"""TASK: {task_info.get('title', lesson.title)}
DESCRIPTION: {task_info.get('description', '')}
DELIVERABLE: {task_info.get('deliverable', '')}
REQUIREMENTS:
{req_list}

LEARNER'S SUBMISSION (Attempt #{attempt_number}):
{combined_content}

Grade this submission against the requirements above."""

    # Call LLM for grading
    llm = get_llm_provider()
    try:
        llm_response = await llm.generate(
            prompt=grading_prompt,
            system_prompt=TASK_GRADING_SYSTEM,
            max_tokens=1024,
            temperature=0.3,
            json_mode=True,
        )
        grade = json.loads(llm_response.content)
    except json.JSONDecodeError:
        logger.error("LLM returned non-JSON grading response: %s", llm_response.content[:200])
        grade = {
            "score": 0,
            "passed": False,
            "feedback": "Grading failed — please try again.",
            "strengths": [],
            "improvements": [],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Grading failed: {str(e)}"
        )

    score = int(grade.get("score", 0))
    passed = score >= PASS_THRESHOLD

    # Save submission record
    submission = ImplementationSubmission(
        lesson_id=lesson_id,
        path_id=path_id,
        user_id=path.user_id,
        attempt_number=attempt_number,
        artifact_text=artifact_text[:10_000],
        file_names=file_names,
        extracted_content=all_extracted[:10_000],
        score=score,
        passed=passed,
        feedback=grade.get("feedback", ""),
        strengths=grade.get("strengths", [])[:3],
        improvements=grade.get("improvements", [])[:3],
    )
    db.add(submission)
    await db.commit()

    # Update Skill Genome with project evidence
    if module:
        try:
            genome_svc = SkillGenomeService()
            await genome_svc.update_from_project(
                db, path.user_id, module.skill_id, feedback_quality=score / 100.0,
            )
            await db.commit()
        except Exception:
            pass  # Non-blocking

    return ImplementationTaskGradeResponse(
        score=score,
        passed=passed,
        feedback=grade.get("feedback", ""),
        strengths=grade.get("strengths", [])[:3],
        improvements=grade.get("improvements", [])[:3],
        attempt_number=attempt_number,
    )
