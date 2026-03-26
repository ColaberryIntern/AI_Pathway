"""Profile API routes - CRUD with database storage."""
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.api.deps import get_database
from app.models.profile import Profile
from app.models.user import User
from app.models.goal import Goal
from app.models.skill_gap import SkillGap
from app.models.learning_path import LearningPath
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.progress import Progress
from app.models.skill_mastery import SkillMastery
from app.models.mentor_conversation import MentorConversation
from app.models.implementation_submission import ImplementationSubmission
from app.services.resume_parser import parse_resume
from app.services.jd_profile_parser import parse_jd_profile

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """Parse a resume PDF/DOCX and extract profile fields."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".doc"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Please upload a PDF or DOCX file.",
        )
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")
    try:
        result = await parse_resume(contents, file.filename)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Resume parsing failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to parse resume. Please try again.")


@router.post("/parse-jd-profile")
async def parse_jd_profile_endpoint(body: dict):
    """Parse a job description and extract a structured target profile."""
    jd_text = body.get("jd_text", "")
    target_role = body.get("target_role", "")
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="No job description text provided.")
    try:
        result = await parse_jd_profile(jd_text, target_role)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("JD profile parsing failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to parse job description. Please try again.")


# ──────────────────────────────────────────────────────────
# CRUD Endpoints - Database-backed profiles
# ──────────────────────────────────────────────────────────


@router.get("/")
async def list_profiles(db: AsyncSession = Depends(get_database)):
    """List all saved profiles with summary status (analysis, learning path, progress)."""
    result = await db.execute(
        select(Profile).order_by(Profile.created_at.desc())
    )
    profiles = result.scalars().all()

    enriched = []
    for p in profiles:
        # Check for linked analysis/learning path
        goal_result = await db.execute(
            select(Goal).where(Goal.profile_id == p.id).order_by(Goal.created_at.desc())
        )
        goal = goal_result.scalars().first()

        learning_path = None
        overall_progress = 0
        lessons_completed = 0
        total_lessons = 0

        if goal:
            lp_result = await db.execute(
                select(LearningPath).where(LearningPath.goal_id == goal.id).order_by(LearningPath.created_at.desc())
            )
            learning_path = lp_result.scalars().first()

            if learning_path:
                # Count lessons
                total_result = await db.execute(
                    select(func.count(Lesson.id)).where(Lesson.path_id == learning_path.id)
                )
                total_lessons = total_result.scalar() or 0

                completed_result = await db.execute(
                    select(func.count(Lesson.id)).where(
                        Lesson.path_id == learning_path.id,
                        Lesson.status == "completed",
                    )
                )
                lessons_completed = completed_result.scalar() or 0

                if total_lessons > 0:
                    overall_progress = round(lessons_completed / total_lessons * 100)

        profile_data = p.profile_data or {}

        enriched.append({
            "id": p.id,
            "name": p.name,
            "current_role": p.current_role,
            "target_role": p.target_role,
            "industry": p.industry,
            "experience_years": p.experience_years,
            "ai_exposure_level": p.ai_exposure_level,
            "learning_intent": p.learning_intent,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            # Status fields
            "has_analysis": goal is not None,
            "has_learning_path": learning_path is not None,
            "learning_path_id": learning_path.id if learning_path else None,
            "goal_id": goal.id if goal else None,
            "user_id": p.user_id,
            "overall_progress": overall_progress,
            "lessons_completed": lessons_completed,
            "total_lessons": total_lessons,
            # Profile display fields
            "tools_used": profile_data.get("tools_used", []),
            "technical_background": profile_data.get("technical_background", ""),
            "current_profile": profile_data.get("current_profile"),
        })

    return enriched


@router.get("/{profile_id}")
async def get_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get a full profile with all linked data."""
    p = await db.get(Profile, profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = p.profile_data or {}

    # Get linked goal/learning path
    goal_result = await db.execute(
        select(Goal).where(Goal.profile_id == p.id).order_by(Goal.created_at.desc())
    )
    goal = goal_result.scalars().first()

    learning_path_id = None
    if goal:
        lp_result = await db.execute(
            select(LearningPath).where(LearningPath.goal_id == goal.id).order_by(LearningPath.created_at.desc())
        )
        lp = lp_result.scalars().first()
        if lp:
            learning_path_id = lp.id

    return {
        "id": p.id,
        "name": p.name,
        "current_role": p.current_role,
        "target_role": p.target_role,
        "industry": p.industry,
        "experience_years": p.experience_years,
        "ai_exposure_level": p.ai_exposure_level,
        "learning_intent": p.learning_intent,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "user_id": p.user_id,
        "goal_id": goal.id if goal else None,
        "learning_path_id": learning_path_id,
        # Full profile data for analysis page
        "tools_used": profile_data.get("tools_used", []),
        "technical_background": profile_data.get("technical_background", ""),
        "current_profile": profile_data.get("current_profile"),
        "target_jd": profile_data.get("target_jd"),
        "target_jd_text": profile_data.get("target_jd_text", ""),
        "estimated_current_skills": profile_data.get("estimated_current_skills"),
        "expected_skill_gaps": profile_data.get("expected_skill_gaps"),
        "archetype": profile_data.get("archetype"),
        "profile_data": profile_data,
    }


@router.post("/")
async def create_profile(
    body: dict,
    db: AsyncSession = Depends(get_database),
):
    """Create a new profile and save to database.

    Accepts the full profile object. Stores structured fields in columns
    and everything else in profile_data JSON.
    """
    name = body.get("name", "")
    if not name.strip():
        raise HTTPException(status_code=400, detail="Name is required.")

    # Create user for this profile
    user = User(name=name)
    db.add(user)
    await db.flush()

    # Extract structured fields for columns, store rest in profile_data
    profile_data = {
        "current_profile": body.get("current_profile"),
        "tools_used": body.get("tools_used", []),
        "technical_background": body.get("technical_background", ""),
        "archetype": body.get("archetype"),
        "target_jd": body.get("target_jd"),
        "target_jd_text": body.get("target_jd_text", ""),
        "estimated_current_skills": body.get("estimated_current_skills"),
        "expected_skill_gaps": body.get("expected_skill_gaps"),
    }

    db_profile = Profile(
        user_id=user.id,
        source="custom",
        name=name,
        current_role=body.get("current_role", ""),
        target_role=body.get("target_role", ""),
        industry=body.get("industry", ""),
        experience_years=body.get("experience_years"),
        ai_exposure_level=body.get("ai_exposure_level"),
        learning_intent=body.get("learning_intent"),
        profile_data=profile_data,
    )
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)

    return {
        "id": db_profile.id,
        "user_id": user.id,
        "name": db_profile.name,
        "message": "Profile created successfully",
    }


@router.put("/{profile_id}")
async def update_profile(
    profile_id: str,
    body: dict,
    db: AsyncSession = Depends(get_database),
):
    """Update an existing profile."""
    p = await db.get(Profile, profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update column fields if provided
    for field in ("name", "current_role", "target_role", "industry",
                  "experience_years", "ai_exposure_level", "learning_intent"):
        if field in body:
            setattr(p, field, body[field])

    # Update profile_data JSON fields
    profile_data = p.profile_data or {}
    for field in ("current_profile", "tools_used", "technical_background",
                  "archetype", "target_jd", "target_jd_text",
                  "estimated_current_skills", "expected_skill_gaps"):
        if field in body:
            profile_data[field] = body[field]
    p.profile_data = profile_data

    await db.commit()
    return {"id": p.id, "message": "Profile updated successfully"}


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Delete a profile and all linked records (cascade)."""
    p = await db.get(Profile, profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")

    user_id = p.user_id

    # Delete linked records in dependency order
    if user_id:
        # Get all learning paths for this user
        lp_result = await db.execute(
            select(LearningPath.id).where(LearningPath.user_id == user_id)
        )
        path_ids = [row[0] for row in lp_result.all()]

        for path_id in path_ids:
            # Delete lessons, modules, progress, mastery, mentoring, submissions
            await db.execute(delete(ImplementationSubmission).where(ImplementationSubmission.path_id == path_id))
            await db.execute(delete(MentorConversation).where(MentorConversation.path_id == path_id))
            await db.execute(delete(Lesson).where(Lesson.path_id == path_id))
            await db.execute(delete(Module).where(Module.path_id == path_id))
            await db.execute(delete(Progress).where(Progress.path_id == path_id))
            await db.execute(delete(SkillMastery).where(SkillMastery.path_id == path_id))

        await db.execute(delete(LearningPath).where(LearningPath.user_id == user_id))
        await db.execute(delete(SkillGap).where(SkillGap.user_id == user_id))
        await db.execute(delete(Goal).where(Goal.user_id == user_id))

    await db.delete(p)

    # Delete the user record too
    if user_id:
        user = await db.get(User, user_id)
        if user:
            await db.delete(user)

    await db.commit()
    return {"message": "Profile deleted successfully"}


# Keep legacy upload endpoint for backward compatibility
@router.post("/upload", response_model=dict)
async def upload_profile(body: dict, db: AsyncSession = Depends(get_database)):
    """Upload a custom profile (legacy endpoint, redirects to create)."""
    return await create_profile(body, db)
