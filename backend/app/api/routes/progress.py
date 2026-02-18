"""Progress tracking API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_database
from app.models.progress import Progress
from app.models.learning_path import LearningPath
from app.schemas.progress import ProgressCreate, ProgressUpdate

router = APIRouter()


@router.post("/")
async def create_progress(
    request: ProgressCreate,
    db: AsyncSession = Depends(get_database),
):
    """Create progress tracking for a learning path."""
    # Verify path exists
    result = await db.execute(
        select(LearningPath).where(LearningPath.id == request.path_id)
    )
    learning_path = result.scalars().first()

    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    # Check if progress already exists
    result = await db.execute(
        select(Progress).where(Progress.path_id == request.path_id)
    )
    existing = result.scalars().first()

    if existing:
        return {
            "id": existing.id,
            "message": "Progress tracking already exists",
        }

    # Create initial progress
    chapter_status = {str(i): "not_started" for i in range(1, learning_path.total_chapters + 1)}
    chapter_status["1"] = "in_progress"

    progress = Progress(
        user_id=learning_path.user_id,
        path_id=request.path_id,
        current_chapter=1,
        chapter_status=chapter_status,
        quiz_scores={},
    )
    db.add(progress)
    await db.commit()
    await db.refresh(progress)

    return {
        "id": progress.id,
        "current_chapter": progress.current_chapter,
        "chapter_status": progress.chapter_status,
    }


@router.put("/{path_id}")
async def update_progress(
    path_id: str,
    request: ProgressUpdate,
    db: AsyncSession = Depends(get_database),
):
    """Update progress for a learning path."""
    result = await db.execute(
        select(Progress).where(Progress.path_id == path_id)
    )
    progress = result.scalars().first()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    # Update chapter status (copy dict so SQLAlchemy detects the change)
    chapter_status = dict(progress.chapter_status or {})
    chapter_status[str(request.chapter)] = request.status

    # Update quiz score if provided (copy dict for same reason)
    quiz_scores = dict(progress.quiz_scores or {})
    if request.quiz_score is not None:
        quiz_scores[str(request.chapter)] = request.quiz_score

    # Auto-advance current chapter if completed
    if request.status == "completed":
        next_chapter = request.chapter + 1
        if str(next_chapter) in chapter_status:
            if chapter_status.get(str(next_chapter)) == "not_started":
                chapter_status[str(next_chapter)] = "in_progress"
            progress.current_chapter = next_chapter

    progress.chapter_status = chapter_status
    progress.quiz_scores = quiz_scores
    await db.commit()

    return {
        "id": progress.id,
        "current_chapter": progress.current_chapter,
        "chapter_status": progress.chapter_status,
        "quiz_scores": progress.quiz_scores,
    }


@router.get("/{path_id}")
async def get_progress(
    path_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get progress for a learning path."""
    result = await db.execute(
        select(Progress).where(Progress.path_id == path_id)
    )
    progress = result.scalars().first()

    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")

    # Calculate completion percentage
    chapter_status = progress.chapter_status or {}
    completed = sum(1 for s in chapter_status.values() if s == "completed")
    total = len(chapter_status)
    completion_pct = (completed / total * 100) if total > 0 else 0

    return {
        "id": progress.id,
        "path_id": progress.path_id,
        "current_chapter": progress.current_chapter,
        "chapter_status": progress.chapter_status,
        "quiz_scores": progress.quiz_scores,
        "completion_percentage": round(completion_pct, 1),
        "updated_at": progress.updated_at.isoformat(),
    }


@router.get("/user/{user_id}/dashboard")
async def get_user_dashboard(
    user_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get user dashboard with all learning progress."""
    # Get all user's paths with progress
    result = await db.execute(
        select(LearningPath).where(LearningPath.user_id == user_id)
    )
    paths = result.scalars().all()

    active_paths = []
    completed_paths = []
    total_skills_learned = 0

    for path in paths:
        # Get progress
        progress_result = await db.execute(
            select(Progress).where(Progress.path_id == path.id)
        )
        progress = progress_result.scalars().first()

        chapter_status = progress.chapter_status if progress else {}
        completed_chapters = sum(1 for s in chapter_status.values() if s == "completed")
        total_chapters = path.total_chapters

        path_data = {
            "id": path.id,
            "title": path.title,
            "total_chapters": total_chapters,
            "completed_chapters": completed_chapters,
            "completion_percentage": round(completed_chapters / total_chapters * 100, 1) if total_chapters > 0 else 0,
            "created_at": path.created_at.isoformat(),
        }

        if completed_chapters == total_chapters and total_chapters > 0:
            completed_paths.append(path_data)
            total_skills_learned += total_chapters
        else:
            active_paths.append(path_data)

    return {
        "user_id": user_id,
        "active_paths": active_paths,
        "completed_paths": completed_paths,
        "total_skills_learned": total_skills_learned,
        "total_paths": len(paths),
    }
