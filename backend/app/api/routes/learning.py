"""Learning execution API routes — activate, dashboard, lessons, skill mastery."""
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_database
from app.models.learning_path import LearningPath
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.skill_mastery import SkillMastery
from app.services.skill_genome import SkillGenomeService
from app.models.goal import Goal
from app.agents.module_outline import ModuleOutlineAgent
from app.agents.lesson_generator import LessonGeneratorAgent
from app.schemas.learning import (
    ActivatePathResponse,
    LearningDashboardResponse,
    LessonCompleteRequest,
    LessonCompleteResponse,
    LessonOutline,
    LessonResponse,
    ModuleResponse,
    SkillMasteryResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────────

def _module_status(module: Module, lessons: list[Lesson]) -> str:
    """Derive module status from its lessons."""
    module_lessons = [l for l in lessons if l.module_id == module.id]
    if not module_lessons:
        return "not_started"
    completed = sum(1 for l in module_lessons if l.status == "completed")
    if completed == len(module_lessons):
        return "completed"
    if any(l.status in ("in_progress", "completed") for l in module_lessons):
        return "in_progress"
    return "not_started"


def _module_response(module: Module, lessons: list[Lesson]) -> ModuleResponse:
    """Build a ModuleResponse from a Module and its lessons."""
    module_lessons = [l for l in lessons if l.module_id == module.id]
    completed = sum(1 for l in module_lessons if l.status == "completed")

    # Enrich lesson outlines with DB lesson IDs so the frontend can link to any lesson
    lesson_id_map = {l.lesson_number: l.id for l in module_lessons}
    enriched_outline = None
    if module.lesson_outline:
        enriched_outline = []
        for outline in module.lesson_outline:
            entry = dict(outline)
            entry["id"] = lesson_id_map.get(outline.get("lesson_number"))
            enriched_outline.append(entry)

    return ModuleResponse(
        id=module.id,
        chapter_number=module.chapter_number,
        skill_id=module.skill_id,
        skill_name=module.skill_name,
        title=module.title,
        current_level=module.current_level,
        target_level=module.target_level,
        lesson_outline=enriched_outline,
        total_lessons=module.total_lessons,
        completed_lessons=completed,
        status=_module_status(module, lessons),
    )


def _mastery_response(m: SkillMastery) -> SkillMasteryResponse:
    """Build a SkillMasteryResponse from a SkillMastery record."""
    progress = 0.0
    if m.target_level > m.initial_level:
        progress = (m.current_level - m.initial_level) / (m.target_level - m.initial_level) * 100
    return SkillMasteryResponse(
        skill_id=m.skill_id,
        skill_name=m.skill_name,
        initial_level=m.initial_level,
        current_level=m.current_level,
        target_level=m.target_level,
        lessons_completed=m.lessons_completed,
        total_lessons=m.total_lessons,
        avg_quiz_score=m.avg_quiz_score,
        progress_percentage=round(max(0.0, min(100.0, progress)), 1),
    )


# ── POST /activate ───────────────────────────────────────────────────

@router.post("/{path_id}/activate", response_model=ActivatePathResponse)
async def activate_learning_path(
    path_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Activate a learning path — creates modules, lesson outlines, and skill mastery records.

    Idempotent: returns existing data if already activated.
    """
    # 1. Verify path exists
    result = await db.execute(
        select(LearningPath).where(LearningPath.id == path_id)
    )
    path = result.scalars().first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    # 2. Check if already activated (modules exist)
    result = await db.execute(
        select(Module).where(Module.path_id == path_id)
    )
    existing_modules = result.scalars().all()
    if existing_modules:
        # Already activated — return existing data
        result = await db.execute(
            select(Lesson).where(Lesson.path_id == path_id)
        )
        all_lessons = result.scalars().all()
        result = await db.execute(
            select(SkillMastery).where(SkillMastery.path_id == path_id)
        )
        masteries = result.scalars().all()

        modules_resp = [_module_response(m, all_lessons) for m in sorted(existing_modules, key=lambda m: m.chapter_number)]
        return ActivatePathResponse(
            modules=modules_resp,
            total_lessons=len(all_lessons),
            skill_masteries=[_mastery_response(m) for m in masteries],
        )

    # 3. Parse chapters from the learning path JSON
    chapters = path.chapters
    if not chapters:
        raise HTTPException(status_code=400, detail="Learning path has no chapters")

    # Normalize: chapters could be a list or a dict with a "chapters" key
    if isinstance(chapters, dict):
        chapters = chapters.get("chapters", [])

    # 4. Get learner context from the goal
    learner_context = {"industry": "General", "profile_summary": ""}
    if path.goal_id:
        result = await db.execute(select(Goal).where(Goal.id == path.goal_id))
        goal = result.scalars().first()
        if goal:
            learner_context["target_role"] = goal.target_role or ""

    # 5. Create Module + Lesson + SkillMastery records
    # New format: 1 chapter = 1 lesson (15-minute interactive chapter)
    # No multi-lesson outlines needed - content generated on demand
    all_modules = []
    all_lessons = []
    all_masteries = []

    logger.info("Creating %d modules (1 chapter per skill level)...", len(chapters))

    for i, chapter in enumerate(chapters):
        chapter_num = chapter.get("chapter_number", i + 1)
        skill_id = chapter.get("skill_id", chapter.get("primary_skill_id", f"unknown_{i}"))
        skill_name = chapter.get("skill_name", chapter.get("primary_skill_name", "Unknown"))
        title = chapter.get("title", f"Module {chapter_num}")
        current_level = chapter.get("current_level", 0)
        target_level = chapter.get("target_level", 1)

        # Single lesson per module (15-minute chapter)
        lesson_outline = [
            {
                "lesson_number": 1,
                "title": f"{skill_name}: L{current_level} to L{target_level}",
                "type": "chapter",
                "focus_area": f"Level {current_level} to {target_level}",
                "estimated_minutes": 15,
            }
        ]
        total_lessons = 1

        # Create Module
        module = Module(
            path_id=path_id,
            chapter_number=chapter_num,
            skill_id=skill_id,
            skill_name=skill_name,
            title=title,
            current_level=current_level,
            target_level=target_level,
            lesson_outline=lesson_outline,
            total_lessons=total_lessons,
        )
        db.add(module)
        await db.flush()  # get the module.id
        all_modules.append(module)

        # Create Lesson records (content=null, generated on-demand)
        for lesson_info in lesson_outline:
            lesson = Lesson(
                module_id=module.id,
                path_id=path_id,
                lesson_number=lesson_info.get("lesson_number", 1),
                title=lesson_info.get("title", "Untitled"),
                lesson_type=lesson_info.get("type", "concept"),
                content=None,
                status="not_started",
            )
            db.add(lesson)
            all_lessons.append(lesson)

        # Create SkillMastery record
        mastery = SkillMastery(
            user_id=path.user_id,
            path_id=path_id,
            skill_id=skill_id,
            skill_name=skill_name,
            initial_level=current_level,
            current_level=float(current_level),
            target_level=target_level,
            lessons_completed=0,
            total_lessons=total_lessons,
        )
        db.add(mastery)
        all_masteries.append(mastery)

    # Migrate lesson content from previous path (preserve already-generated curriculum)
    if path.previous_path_id:
        try:
            # Get previous path's modules indexed by skill_id
            prev_modules_q = await db.execute(
                select(Module).where(Module.path_id == path.previous_path_id)
            )
            prev_modules = {m.skill_id: m for m in prev_modules_q.scalars().all()}

            migrated_count = 0
            for new_module in all_modules:
                prev_module = prev_modules.get(new_module.skill_id)
                if not prev_module:
                    continue
                # Get previous lessons with content for this module
                prev_lessons_q = await db.execute(
                    select(Lesson)
                    .where(Lesson.module_id == prev_module.id)
                    .where(Lesson.content.isnot(None))
                )
                prev_lessons_by_num = {
                    l.lesson_number: l for l in prev_lessons_q.scalars().all()
                }
                # Copy content to matching new lessons
                for new_lesson in all_lessons:
                    if new_lesson.module_id == new_module.id:
                        prev_lesson = prev_lessons_by_num.get(new_lesson.lesson_number)
                        if prev_lesson and prev_lesson.content:
                            new_lesson.content = prev_lesson.content
                            new_lesson.status = prev_lesson.status
                            migrated_count += 1

            if migrated_count > 0:
                logger.info("Migrated %d lesson(s) from previous path %s", migrated_count, path.previous_path_id)
        except Exception as e:
            logger.warning("Lesson migration failed (non-fatal): %s", e)

    await db.commit()

    # Refresh all to get generated IDs
    for obj in all_modules + all_lessons + all_masteries:
        await db.refresh(obj)

    modules_resp = [_module_response(m, all_lessons) for m in sorted(all_modules, key=lambda m: m.chapter_number)]
    return ActivatePathResponse(
        modules=modules_resp,
        total_lessons=len(all_lessons),
        skill_masteries=[_mastery_response(m) for m in all_masteries],
    )


# ── GET /dashboard ───────────────────────────────────────────────────

@router.get("/{path_id}/dashboard", response_model=LearningDashboardResponse)
async def get_learning_dashboard(
    path_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get the full learning dashboard for a path."""
    # Load path
    result = await db.execute(
        select(LearningPath).where(LearningPath.id == path_id)
    )
    path = result.scalars().first()
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    # Load modules
    result = await db.execute(
        select(Module).where(Module.path_id == path_id)
    )
    modules = sorted(result.scalars().all(), key=lambda m: m.chapter_number)

    if not modules:
        raise HTTPException(
            status_code=400,
            detail="Learning path not yet activated. Call POST /activate first.",
        )

    # Load all lessons
    result = await db.execute(
        select(Lesson).where(Lesson.path_id == path_id)
    )
    all_lessons = result.scalars().all()

    # Load skill masteries
    result = await db.execute(
        select(SkillMastery).where(SkillMastery.path_id == path_id)
    )
    masteries = result.scalars().all()

    # Get target role from goal
    target_role = ""
    if path.goal_id:
        result = await db.execute(select(Goal).where(Goal.id == path.goal_id))
        goal = result.scalars().first()
        if goal:
            target_role = goal.target_role or ""

    # Build module responses
    module_responses = [_module_response(m, all_lessons) for m in modules]

    # Overall progress
    total_lessons = len(all_lessons)
    completed_lessons = sum(1 for l in all_lessons if l.status == "completed")
    overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

    # Find current module (first non-completed) and next lesson
    current_module = None
    next_lesson_outline = None
    next_lesson_id = None

    for mod_resp, mod in zip(module_responses, modules):
        if mod_resp.status != "completed":
            current_module = mod_resp
            # Find next uncompleted lesson in this module
            mod_lessons = sorted(
                [l for l in all_lessons if l.module_id == mod.id],
                key=lambda l: l.lesson_number,
            )
            for lesson in mod_lessons:
                if lesson.status != "completed":
                    next_lesson_id = lesson.id
                    # Find matching outline entry
                    if mod.lesson_outline:
                        for outline in mod.lesson_outline:
                            if outline.get("lesson_number") == lesson.lesson_number:
                                next_lesson_outline = LessonOutline(**outline)
                                break
                    break
            break

    # Estimated hours remaining
    total_mins = 0
    for mod in modules:
        mod_lessons = [l for l in all_lessons if l.module_id == mod.id]
        for lesson in mod_lessons:
            if lesson.status != "completed" and mod.lesson_outline:
                for outline in mod.lesson_outline:
                    if outline.get("lesson_number") == lesson.lesson_number:
                        total_mins += outline.get("estimated_minutes", 30)
    estimated_hours = round(total_mins / 60, 1)

    return LearningDashboardResponse(
        path_id=path.id,
        path_title=path.title or "Learning Path",
        target_role=target_role,
        overall_progress=round(overall_progress, 1),
        modules=module_responses,
        skill_masteries=[_mastery_response(m) for m in masteries],
        current_module=current_module,
        next_lesson=next_lesson_outline,
        next_lesson_id=next_lesson_id,
        total_lessons_completed=completed_lessons,
        total_lessons=total_lessons,
        estimated_hours_remaining=estimated_hours,
    )


# ── GET /modules ─────────────────────────────────────────────────────

@router.get("/{path_id}/modules", response_model=list[ModuleResponse])
async def get_modules(
    path_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get all modules for a learning path."""
    result = await db.execute(
        select(Module).where(Module.path_id == path_id)
    )
    modules = sorted(result.scalars().all(), key=lambda m: m.chapter_number)

    result = await db.execute(
        select(Lesson).where(Lesson.path_id == path_id)
    )
    all_lessons = result.scalars().all()

    return [_module_response(m, all_lessons) for m in modules]


def _has_substance(content: dict) -> bool:
    """Check that cached lesson content has actual educational material."""
    return bool(
        content.get("concept_snapshot")
        or content.get("explanation")
        or content.get("knowledge_checks")
    )


# ── POST /lessons/{lesson_id}/start ──────────────────────────────────

@router.post("/{path_id}/lessons/{lesson_id}/start", response_model=LessonResponse)
async def start_lesson(
    path_id: str,
    lesson_id: str,
    regenerate: bool = False,
    db: AsyncSession = Depends(get_database),
):
    """Start a lesson — generates content on-demand if not yet cached."""
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.path_id == path_id)
    )
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Force re-generation if requested (clears stale empty content)
    if regenerate:
        lesson.content = None
        await db.commit()

    # If content already exists and has substance, return immediately
    if lesson.content is not None and _has_substance(lesson.content):
        if lesson.status == "not_started":
            lesson.status = "in_progress"
            await db.commit()
        return LessonResponse(
            id=lesson.id,
            module_id=lesson.module_id,
            lesson_number=lesson.lesson_number,
            title=lesson.title,
            lesson_type=lesson.lesson_type,
            content=lesson.content,
            status=lesson.status,
            quiz_score=lesson.quiz_score,
            exercise_attempts=lesson.exercise_attempts,
        )

    # Generate content on-demand
    result = await db.execute(
        select(Module).where(Module.id == lesson.module_id)
    )
    module = result.scalars().first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get preceding lesson titles for context
    result = await db.execute(
        select(Lesson).where(
            Lesson.module_id == module.id,
            Lesson.lesson_number < lesson.lesson_number,
        )
    )
    preceding_lessons = result.scalars().all()
    preceding_titles = [l.title for l in sorted(preceding_lessons, key=lambda l: l.lesson_number)]

    # Get learner context (industry, target role, profile summary)
    result = await db.execute(
        select(LearningPath).where(LearningPath.id == path_id)
    )
    path = result.scalars().first()
    learner_context: dict = {"industry": "General", "target_role": "", "profile_summary": ""}
    if path and path.goal_id:
        result = await db.execute(select(Goal).where(Goal.id == path.goal_id))
        goal = result.scalars().first()
        if goal:
            learner_context["target_role"] = goal.target_role or ""
            learner_context["target_jd"] = goal.target_jd_text or ""
            # Get industry from linked profile
            if goal.profile_id:
                from app.models.profile import Profile as ProfileModel
                profile = await db.get(ProfileModel, goal.profile_id)
                if profile:
                    learner_context["industry"] = profile.industry or "General"
                    pd = profile.profile_data or {}
                    learner_context["technical_background"] = pd.get("technical_background") or ""
                    learner_context["profile_summary"] = (
                        (pd.get("current_profile") or {}).get("summary") or ""
                    )

    # Find focus area from lesson outline
    focus_area = ""
    if module.lesson_outline:
        for outline in module.lesson_outline:
            if outline.get("lesson_number") == lesson.lesson_number:
                focus_area = outline.get("focus_area", "")
                break

    logger.info("Generating content for lesson '%s' (module: %s)...", lesson.title, module.title)

    try:
        # Use ChapterGeneratorAgent for single-lesson modules (Vivek's format)
        # Fall back to LessonGeneratorAgent for multi-lesson modules (legacy)
        if module.total_lessons == 1:
            from app.agents.chapter_generator import ChapterGeneratorAgent
            generator = ChapterGeneratorAgent()
            gen_result = await generator.execute({
                "skill_id": module.skill_id,
                "current_level": module.current_level,
                "target_level": module.target_level,
                "learner_context": learner_context,
            })
        else:
            generator = LessonGeneratorAgent()
            gen_result = await generator.execute({
                "module": {
                    "skill_id": module.skill_id,
                    "skill_name": module.skill_name,
                    "title": module.title,
                    "current_level": module.current_level,
                    "target_level": module.target_level,
                },
                "lesson_number": lesson.lesson_number,
                "lesson_title": lesson.title,
                "lesson_type": lesson.lesson_type,
                "lesson_focus_area": focus_area,
                "learner_context": learner_context,
                "module_context": {
                    "total_lessons": module.total_lessons,
                    "lesson_outline": module.lesson_outline,
                    "preceding_lesson_titles": preceding_titles,
                },
            })
    except Exception as e:
        logger.error("Lesson generation failed (lesson_id=%s): %s", lesson.id, e)
        raise HTTPException(
            status_code=502,
            detail=f"Lesson content generation failed: {str(e)[:200]}",
        )

    content = gen_result.get("content", {})

    # Don't cache empty shells — let subsequent visits retry generation
    if not _has_substance(content):
        logger.warning(
            "Lesson generation returned empty content (lesson_id=%s)", lesson.id,
        )
        raise HTTPException(
            status_code=502,
            detail="Lesson content generation returned empty content. Please retry.",
        )

    # Validate and auto-fix Python code examples
    try:
        from app.services.code_validator import validate_and_fix_code_examples
        content = await validate_and_fix_code_examples(content, agent.llm.generate)
    except Exception as e:
        logger.warning("Code validation step failed (non-fatal): %s", e)

    # Cache generated content
    lesson.content = content
    lesson.status = "in_progress"
    await db.commit()
    await db.refresh(lesson)

    logger.info("Lesson content generated and cached (lesson_id=%s)", lesson.id)

    return LessonResponse(
        id=lesson.id,
        module_id=lesson.module_id,
        lesson_number=lesson.lesson_number,
        title=lesson.title,
        lesson_type=lesson.lesson_type,
        content=lesson.content,
        status=lesson.status,
        quiz_score=lesson.quiz_score,
        exercise_attempts=lesson.exercise_attempts,
    )


# ── PUT /lessons/{lesson_id}/complete ────────────────────────────────

@router.put("/{path_id}/lessons/{lesson_id}/complete")
async def complete_lesson(
    path_id: str,
    lesson_id: str,
    request: LessonCompleteRequest,
    db: AsyncSession = Depends(get_database),
):
    """Mark a lesson as complete and update skill mastery."""
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.path_id == path_id)
    )
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Update lesson
    lesson.status = "completed"
    lesson.completed_at = datetime.utcnow()
    if request.quiz_score is not None:
        lesson.quiz_score = request.quiz_score

    # Get path (for user_id)
    result = await db.execute(
        select(LearningPath).where(LearningPath.id == path_id)
    )
    path = result.scalars().first()

    # Get module
    result = await db.execute(
        select(Module).where(Module.id == lesson.module_id)
    )
    module = result.scalars().first()

    # Update skill mastery
    mastery_update = None
    if module:
        result = await db.execute(
            select(SkillMastery).where(
                SkillMastery.path_id == path_id,
                SkillMastery.skill_id == module.skill_id,
            )
        )
        mastery = result.scalars().first()
        if mastery:
            mastery.lessons_completed += 1
            # Update current level proportionally
            if mastery.total_lessons > 0:
                progress_fraction = mastery.lessons_completed / mastery.total_lessons
                mastery.current_level = mastery.initial_level + (
                    (mastery.target_level - mastery.initial_level) * progress_fraction
                )

            # Update avg quiz score
            if request.quiz_score is not None:
                result = await db.execute(
                    select(Lesson).where(
                        Lesson.module_id == module.id,
                        Lesson.quiz_score.isnot(None),
                    )
                )
                scored_lessons = result.scalars().all()
                scores = [l.quiz_score for l in scored_lessons if l.quiz_score is not None]
                scores.append(request.quiz_score)
                mastery.avg_quiz_score = sum(scores) / len(scores) if scores else None

            mastery_update = _mastery_response(mastery)

    # Update global Skill Genome
    if module:
        try:
            genome_svc = SkillGenomeService()
            await genome_svc.update_from_lesson(
                db,
                path.user_id,
                module.skill_id,
                quiz_score=request.quiz_score,
                lesson_type=lesson.lesson_type,
            )
        except Exception as e:
            logger.warning("Skill Genome update failed (non-blocking): %s", e)

    await db.commit()

    # Build module progress response
    result = await db.execute(
        select(Lesson).where(Lesson.path_id == path_id)
    )
    all_lessons = result.scalars().all()

    lesson_resp = LessonResponse(
        id=lesson.id,
        module_id=lesson.module_id,
        lesson_number=lesson.lesson_number,
        title=lesson.title,
        lesson_type=lesson.lesson_type,
        content=lesson.content,
        status=lesson.status,
        quiz_score=lesson.quiz_score,
        exercise_attempts=lesson.exercise_attempts,
    )

    module_resp = _module_response(module, all_lessons) if module else None

    return {
        "lesson": lesson_resp.model_dump(),
        "module_progress": module_resp.model_dump() if module_resp else None,
        "skill_mastery_update": mastery_update.model_dump() if mastery_update else None,
    }


# ── GET /skills ──────────────────────────────────────────────────────

@router.get("/{path_id}/skills", response_model=list[SkillMasteryResponse])
async def get_skill_masteries(
    path_id: str,
    db: AsyncSession = Depends(get_database),
):
    """Get all skill mastery records for a learning path."""
    result = await db.execute(
        select(SkillMastery).where(SkillMastery.path_id == path_id)
    )
    masteries = result.scalars().all()
    return [_mastery_response(m) for m in masteries]
