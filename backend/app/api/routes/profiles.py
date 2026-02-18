"""Profile API routes."""
import json
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_database
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpload
from app.services.resume_parser import parse_resume

logger = logging.getLogger(__name__)

router = APIRouter()

# Path to test profiles
PROFILES_DIR = Path(__file__).parent.parent.parent / "data" / "profiles"


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


@router.get("/", response_model=list[dict])
async def list_profiles():
    """List all 12 test profiles."""
    profiles = []
    for profile_file in sorted(PROFILES_DIR.glob("profile_*.json")):
        with open(profile_file) as f:
            profile_data = json.load(f)
            profiles.append({
                "id": profile_data["id"],
                "name": profile_data["name"],
                "current_role": profile_data["current_role"],
                "target_role": profile_data["target_role"],
                "industry": profile_data["industry"],
                "experience_years": profile_data.get("experience_years"),
                "ai_exposure_level": profile_data.get("ai_exposure_level"),
                "archetype": profile_data.get("archetype"),
                "learning_intent": profile_data.get("learning_intent"),
                "current_profile": profile_data.get("current_profile"),
            })
    return profiles


@router.get("/{profile_id}")
async def get_profile(profile_id: str):
    """Get a specific test profile by ID."""
    # First try test profiles
    for profile_file in PROFILES_DIR.glob("profile_*.json"):
        with open(profile_file) as f:
            profile_data = json.load(f)
            if profile_data["id"] == profile_id:
                return profile_data

    raise HTTPException(status_code=404, detail="Profile not found")


@router.post("/upload", response_model=dict)
async def upload_profile(
    profile: ProfileUpload,
    db: AsyncSession = Depends(get_database),
):
    """Upload a custom profile."""
    # Create or get anonymous user
    user = User(name=profile.name)
    db.add(user)
    await db.flush()

    # Create profile
    db_profile = Profile(
        user_id=user.id,
        source="custom",
        name=profile.name,
        current_role=profile.current_role,
        target_role=profile.target_role,
        industry=profile.industry,
        experience_years=profile.experience_years,
        ai_exposure_level=profile.ai_exposure_level,
        learning_intent=profile.learning_intent,
        profile_data={
            "current_skills": profile.current_skills,
            "target_jd": profile.target_jd,
        },
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


@router.get("/user/{user_id}/profiles", response_model=list[dict])
async def get_user_profiles(
    user_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get all profiles for a user."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == user_id)
    )
    profiles = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "current_role": p.current_role,
            "target_role": p.target_role,
            "industry": p.industry,
            "created_at": p.created_at.isoformat(),
        }
        for p in profiles
    ]
