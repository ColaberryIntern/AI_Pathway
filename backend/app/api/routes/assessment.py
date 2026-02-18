"""Assessment API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_database
from app.agents.assessment_agent import AssessmentAgent
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentCreate, AssessmentSubmit

router = APIRouter()


@router.post("/generate")
async def generate_assessment(
    request: AssessmentCreate,
    db: AsyncSession = Depends(get_database),
):
    """Generate assessment questions for a user."""
    assessment_agent = AssessmentAgent()

    try:
        result = await assessment_agent.execute({
            "action": "generate",
            "skill_ids": request.skill_ids or [],
            "industry": "",
            "num_questions": 3,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment generation failed: {str(e)}")

    # Save assessment to database
    assessment = Assessment(
        user_id="temp_user",  # Would come from auth
        goal_id=request.goal_id,
        quiz_questions=result.get("questions", []),
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    return {
        "assessment_id": assessment.id,
        "questions": result.get("questions", []),
    }


@router.post("/submit")
async def submit_assessment(
    request: AssessmentSubmit,
    db: AsyncSession = Depends(get_database),
):
    """Submit assessment responses and get scored results."""
    # Get assessment
    result = await db.execute(
        select(Assessment).where(Assessment.id == request.assessment_id)
    )
    assessment = result.scalars().first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Score responses
    assessment_agent = AssessmentAgent()

    try:
        score_result = await assessment_agent.execute({
            "action": "score",
            "questions": assessment.quiz_questions,
            "responses": [r.model_dump() for r in request.responses],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment scoring failed: {str(e)}")

    # Update assessment
    assessment.responses = [r.model_dump() for r in request.responses]
    assessment.state_a_skills = score_result.get("state_a_skills", {})
    from datetime import datetime
    assessment.completed_at = datetime.utcnow()
    await db.commit()

    return {
        "assessment_id": assessment.id,
        "skill_scores": score_result.get("skill_scores", []),
        "state_a_skills": score_result.get("state_a_skills", {}),
    }


@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get assessment details."""
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalars().first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return {
        "id": assessment.id,
        "user_id": assessment.user_id,
        "goal_id": assessment.goal_id,
        "questions": assessment.quiz_questions,
        "responses": assessment.responses,
        "state_a_skills": assessment.state_a_skills,
        "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
    }
