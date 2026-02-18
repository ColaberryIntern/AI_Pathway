"""Learning path API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_database
from app.agents.path_generator import PathGeneratorAgent
from app.agents.content_curator import ContentCuratorAgent
from app.models.learning_path import LearningPath
from app.models.skill_gap import SkillGap
from app.schemas.learning_path import LearningPathCreate
from app.services.path_generator import LearningPathGenerator

router = APIRouter()


@router.post("/generate")
async def generate_learning_path(
    request: LearningPathCreate,
    db: AsyncSession = Depends(get_database),
):
    """Generate a learning path from a skill gap analysis.

    Flow: SkillGap → deterministic scaffold → LLM enrichment → DB.

    The deterministic scaffold (LearningPathGenerator) locks chapter
    count, skill assignments, and level targets.  The LLM agent only
    enriches with objectives, descriptions, exercises, and context.
    """
    # ------------------------------------------------------------------
    # 1. Retrieve the stored skill gap
    # ------------------------------------------------------------------
    result = await db.execute(
        select(SkillGap).where(SkillGap.id == request.gap_id)
    )
    skill_gap = result.scalars().first()

    if not skill_gap:
        raise HTTPException(status_code=404, detail="Skill gap not found")

    # ------------------------------------------------------------------
    # 2. Build State A / State B and generate deterministic scaffold
    # ------------------------------------------------------------------
    gaps_list = skill_gap.gaps or []

    state_a = skill_gap.state_a_skills or {
        g["skill_id"]: g["current_level"] for g in gaps_list
    }
    state_b = skill_gap.state_b_skills or {
        g["skill_id"]: g["target_level"] for g in gaps_list
    }

    try:
        deterministic_generator = LearningPathGenerator()
        deterministic_path = deterministic_generator.generate_path(state_a, state_b)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Deterministic path generation failed: {str(e)}",
        )

    # ------------------------------------------------------------------
    # 3. LLM enrichment — agent receives the locked scaffold
    # ------------------------------------------------------------------
    path_generator = PathGeneratorAgent()

    try:
        path_result = await path_generator.execute({
            "chapter_scaffold": deterministic_path["chapters"],
            "industry": "",
            "learning_intent": "",
            "profile_summary": "",
            "num_chapters": deterministic_path["total_chapters"],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Path generation failed: {str(e)}")

    # ------------------------------------------------------------------
    # 4. Optionally curate content resources
    # ------------------------------------------------------------------
    content_curator = ContentCuratorAgent()
    try:
        resources_result = await content_curator.execute({
            "chapters": path_result.get("chapters", []),
            "industry": "",
        })
        # Merge resources
        for ch_resource in resources_result.get("chapter_resources", []):
            ch_num = ch_resource.get("chapter_number")
            for chapter in path_result.get("chapters", []):
                if chapter.get("chapter_number") == ch_num:
                    chapter["resources"] = ch_resource.get("resources", [])
    except Exception:
        pass  # Resources are optional

    # ------------------------------------------------------------------
    # 5. Persist to database
    # ------------------------------------------------------------------
    learning_path = LearningPath(
        user_id=skill_gap.user_id,
        goal_id=request.goal_id,
        gap_id=skill_gap.id,
        title=path_result.get("title", ""),
        description=path_result.get("description", ""),
        chapters=path_result.get("chapters", []),
        total_chapters=deterministic_path["total_chapters"],
    )
    db.add(learning_path)
    await db.commit()
    await db.refresh(learning_path)

    return {
        "id": learning_path.id,
        "title": learning_path.title,
        "description": learning_path.description,
        "chapters": learning_path.chapters,
        "total_chapters": learning_path.total_chapters,
        "total_estimated_hours": path_result.get("total_estimated_hours", 0),
    }


@router.get("/{path_id}")
async def get_learning_path(
    path_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get a learning path by ID."""
    result = await db.execute(
        select(LearningPath).where(LearningPath.id == path_id)
    )
    learning_path = result.scalars().first()

    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    return {
        "id": learning_path.id,
        "user_id": learning_path.user_id,
        "goal_id": learning_path.goal_id,
        "gap_id": learning_path.gap_id,
        "title": learning_path.title,
        "description": learning_path.description,
        "chapters": learning_path.chapters,
        "total_chapters": learning_path.total_chapters,
        "created_at": learning_path.created_at.isoformat(),
    }


@router.get("/user/{user_id}")
async def get_user_paths(
    user_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get all learning paths for a user."""
    result = await db.execute(
        select(LearningPath)
        .where(LearningPath.user_id == user_id)
        .order_by(LearningPath.created_at.desc())
    )
    paths = result.scalars().all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "total_chapters": p.total_chapters,
            "created_at": p.created_at.isoformat(),
        }
        for p in paths
    ]
