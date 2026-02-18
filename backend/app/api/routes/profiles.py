"""Profile API routes."""
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_database
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpload

router = APIRouter()

# Path to test profiles
PROFILES_DIR = Path(__file__).parent.parent.parent / "data" / "profiles"


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
