"""Analysis API routes - main workflow endpoints."""
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel as _BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_database, get_agent_orchestrator
from app.agents.orchestrator import Orchestrator
from app.agents.jd_parser import JDParserAgent
from app.models.user import User
from app.models.goal import Goal
from app.models.skill_gap import SkillGap
from app.models.learning_path import LearningPath
from app.schemas.analysis import (
    FullAnalysisRequest,
    FullAnalysisResponse,
    JDParseRequest,
    JDParseResponse,
)

router = APIRouter()

PROFILES_DIR = Path(__file__).parent.parent.parent / "data" / "profiles"


def load_test_profile(profile_id: str) -> dict | None:
    """Load a test profile by ID."""
    for profile_file in PROFILES_DIR.glob("profile_*.json"):
        with open(profile_file) as f:
            profile_data = json.load(f)
            if profile_data["id"] == profile_id:
                return profile_data
    return None


@router.post("/full")
async def run_full_analysis(
    request: FullAnalysisRequest,
    db: AsyncSession = Depends(get_database),
    orchestrator: Orchestrator = Depends(get_agent_orchestrator),
):
    """Run full analysis: Profile → JD → Gap → Path generation."""
    # Get or create profile
    if request.profile_id:
        profile = load_test_profile(request.profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
    elif request.custom_profile:
        profile = request.custom_profile
    else:
        raise HTTPException(
            status_code=400,
            detail="Either profile_id or custom_profile must be provided"
        )

    # Run orchestrator OUTSIDE DB transaction (20-40s of LLM calls, no DB lock)
    try:
        result = await orchestrator.execute({
            "profile": profile,
            "jd_text": request.target_jd_text,
            "target_role": request.target_role,
            "skip_assessment": request.skip_assessment,
            "include_resources": True,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Quick DB save — lock held ~100ms instead of 20-40s
    user = User(name=profile.get("name", "Anonymous"))
    db.add(user)
    await db.flush()

    goal = Goal(
        user_id=user.id,
        target_role=request.target_role or profile.get("target_role", ""),
        target_jd_text=request.target_jd_text,
        learning_intent=profile.get("learning_intent", ""),
        state_b_skills=result.get("jd_parsing", {}).get("state_b_skills", {}),
    )
    db.add(goal)
    await db.flush()

    skill_gap = SkillGap(
        user_id=user.id,
        goal_id=goal.id,
        state_a_skills=result.get("profile_analysis", {}).get("state_a_skills", {}),
        state_b_skills=result.get("jd_parsing", {}).get("state_b_skills", {}),
        gaps=result.get("gap_analysis", {}).get("gaps", []),
    )
    db.add(skill_gap)
    await db.flush()

    learning_path = LearningPath(
        user_id=user.id,
        goal_id=goal.id,
        gap_id=skill_gap.id,
        title=result.get("learning_path", {}).get("title", ""),
        description=result.get("learning_path", {}).get("description", ""),
        chapters=result.get("learning_path", {}).get("chapters", []),
        total_chapters=len(result.get("learning_path", {}).get("chapters", [])),
    )
    db.add(learning_path)
    await db.commit()

    return {
        "user_id": user.id,
        "goal_id": goal.id,
        "skill_gap_id": skill_gap.id,
        "learning_path_id": learning_path.id,
        "result": result,
    }


@router.post("/parse-jd", response_model=dict)
async def parse_job_description(request: JDParseRequest):
    """Parse a job description to extract required skills."""
    jd_parser = JDParserAgent()

    try:
        result = await jd_parser.execute({
            "jd_text": request.jd_text,
            "target_role": request.target_role,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")

    return {
        "target_role": request.target_role or result.get("role_analysis", {}).get("primary_function", ""),
        "extracted_skills": result.get("extracted_requirements", []),
        "state_b_skills": result.get("state_b_skills", {}),
        "industry": result.get("industry"),
        "experience_level": result.get("experience_level"),
        "role_analysis": result.get("role_analysis", {}),
    }


@router.get("/gap/{user_id}")
async def get_skill_gap(
    user_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get skill gap analysis for a user."""
    from sqlalchemy import select

    result = await db.execute(
        select(SkillGap)
        .where(SkillGap.user_id == user_id)
        .order_by(SkillGap.created_at.desc())
    )
    skill_gap = result.scalars().first()

    if not skill_gap:
        raise HTTPException(status_code=404, detail="No skill gap found for user")

    return {
        "id": skill_gap.id,
        "state_a_skills": skill_gap.state_a_skills,
        "state_b_skills": skill_gap.state_b_skills,
        "gaps": skill_gap.gaps,
        "created_at": skill_gap.created_at.isoformat(),
    }


class VisualizationRequest(_BaseModel):
    """Accept the analysis result dict for visualization."""

    analysis_result: dict


@router.post("/visualization", response_class=HTMLResponse)
async def generate_visualization(request: VisualizationRequest):
    """Generate a standalone HTML ontology path visualization.

    Accepts the ``result`` field from a completed analysis and returns
    a self-contained HTML page with D3.js interactive graph.
    """
    from app.services.path_visualizer import PathVisualizer

    try:
        visualizer = PathVisualizer()
        html_content = visualizer.generate_html(request.analysis_result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Visualization generation failed: {str(e)}",
        )

    return HTMLResponse(content=html_content)
