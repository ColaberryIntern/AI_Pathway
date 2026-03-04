"""Personalization service — adaptive recommendations from all learning signals."""
import logging
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.skill_genome import SkillGenomeEntry
from app.models.lesson_reaction import LessonReaction
from app.models.lesson import Lesson
from app.models.skill_mastery import SkillMastery
from app.models.module import Module

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Aggregates learning signals into adaptive recommendations."""

    async def get_recommendations(
        self,
        db: AsyncSession,
        user_id: str,
        path_id: str | None = None,
    ) -> dict:
        """Build personalized recommendations from all available signals.

        Signals:
        - SkillGenome mastery levels
        - Lesson reactions (confusion patterns)
        - Quiz scores from completed lessons
        - Lesson completion patterns
        """
        struggling = []
        strong = []
        suggested_review = []

        # 1. Get genome entries
        result = await db.execute(
            select(SkillGenomeEntry).where(SkillGenomeEntry.user_id == user_id)
        )
        genome_entries = result.scalars().all()

        for entry in genome_entries:
            if entry.mastery_level >= 3.0 and entry.confidence >= 0.5:
                strong.append({
                    "skill_name": entry.skill_name,
                    "mastery": round(entry.mastery_level, 2),
                })
            elif entry.mastery_level < 1.5 and entry.evidence_count >= 2:
                struggling.append({
                    "skill_name": entry.skill_name,
                    "signal": "low mastery after multiple lessons",
                })

        # 2. Check confusion signals
        confusion_query = select(
            LessonReaction.lesson_id,
            func.count(LessonReaction.id).label("count"),
        ).where(
            LessonReaction.user_id == user_id,
            LessonReaction.reaction == "confused",
        ).group_by(LessonReaction.lesson_id)

        result = await db.execute(confusion_query)
        confused_lessons = result.all()

        for lesson_id, count in confused_lessons:
            lesson = await db.get(Lesson, lesson_id)
            if lesson and lesson.status != "completed":
                # Get the skill name from the module
                module = await db.get(Module, lesson.module_id)
                skill_name = module.skill_name if module else "Unknown"
                # Only add if not already in struggling list
                if not any(s["skill_name"] == skill_name for s in struggling):
                    struggling.append({
                        "skill_name": skill_name,
                        "signal": "confusion detected",
                    })

        # 3. Find lessons to review (low quiz scores)
        lesson_filter = [Lesson.quiz_score.isnot(None)]
        if path_id:
            lesson_filter.append(Lesson.path_id == path_id)

        result = await db.execute(
            select(Lesson).where(*lesson_filter)
        )
        scored_lessons = result.scalars().all()

        for lesson in scored_lessons:
            if lesson.quiz_score is not None and lesson.quiz_score < 60:
                suggested_review.append({
                    "lesson_id": lesson.id,
                    "title": lesson.title,
                    "reason": f"Quiz score: {lesson.quiz_score}%",
                })

        # 4. Determine pace
        if path_id:
            pace = await self._calculate_pace(db, path_id)
        else:
            pace = "on_track"

        # 5. Determine next focus
        next_focus = None
        if struggling:
            next_focus = {
                "skill_name": struggling[0]["skill_name"],
                "reason": f"Needs attention: {struggling[0]['signal']}",
            }
        elif genome_entries:
            # Find lowest mastery skill that still has room to grow
            lowest = min(
                (e for e in genome_entries if e.mastery_level < 4.0),
                key=lambda e: e.mastery_level,
                default=None,
            )
            if lowest:
                next_focus = {
                    "skill_name": lowest.skill_name,
                    "reason": "Lowest mastery — good area to strengthen",
                }

        return {
            "struggling_skills": struggling[:5],
            "strong_skills": strong[:5],
            "suggested_review": suggested_review[:5],
            "pace_recommendation": pace,
            "next_focus": next_focus,
        }

    async def _calculate_pace(self, db: AsyncSession, path_id: str) -> str:
        """Determine learning pace based on quiz scores and completion rate."""
        result = await db.execute(
            select(SkillMastery).where(SkillMastery.path_id == path_id)
        )
        masteries = result.scalars().all()

        if not masteries:
            return "on_track"

        avg_quiz = [
            m.avg_quiz_score for m in masteries
            if m.avg_quiz_score is not None
        ]
        avg_progress = sum(
            m.lessons_completed / max(1, m.total_lessons) for m in masteries
        ) / len(masteries)

        if avg_quiz and sum(avg_quiz) / len(avg_quiz) < 50:
            return "slow_down"
        elif avg_progress > 0.7 and (not avg_quiz or sum(avg_quiz) / len(avg_quiz) > 80):
            return "can_accelerate"
        return "on_track"
