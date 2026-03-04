"""Skill Genome service — global per-user skill mastery tracking."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.skill_genome import SkillGenomeEntry
from app.services.ontology import get_ontology_service


class SkillGenomeService:
    """Manages the global Skill Genome overlay.

    Mastery is updated via an exponential moving average (EMA):
        new_mastery = weight * current + (1 - weight) * new_signal

    Confidence is derived from evidence volume:
        confidence = min(1.0, evidence_count / 10)
    """

    EMA_WEIGHT = 0.7  # How much existing mastery is retained
    CONFIDENCE_CAP = 10  # Evidence count at which confidence reaches 1.0

    async def update_from_lesson(
        self,
        db: AsyncSession,
        user_id: str,
        skill_id: str,
        quiz_score: float | None = None,
        lesson_type: str = "concept",
    ) -> SkillGenomeEntry:
        """Update genome after a lesson completion.

        Signal strength varies by lesson type and quiz performance.
        """
        # Derive a 0-4 signal from lesson type + quiz score
        base_signal = {"concept": 1.0, "practice": 2.0, "assessment": 3.0}.get(
            lesson_type, 1.5
        )
        if quiz_score is not None:
            # quiz_score is 0-100; scale to 0-4
            base_signal = max(base_signal, quiz_score / 100 * 4.0)

        return await self._upsert(
            db, user_id, skill_id, new_signal=base_signal, evidence_type="lesson"
        )

    async def update_from_project(
        self,
        db: AsyncSession,
        user_id: str,
        skill_id: str,
        feedback_quality: float = 0.5,
    ) -> SkillGenomeEntry:
        """Update genome after a project/implementation task submission.

        feedback_quality is 0.0-1.0 derived from strengths/improvements ratio.
        """
        # Scale quality to 0-4 signal (projects are high-signal evidence)
        signal = feedback_quality * 4.0
        return await self._upsert(
            db, user_id, skill_id, new_signal=signal, evidence_type="project"
        )

    async def get_genome(
        self, db: AsyncSession, user_id: str
    ) -> list[SkillGenomeEntry]:
        """Get all genome entries for a user."""
        result = await db.execute(
            select(SkillGenomeEntry).where(SkillGenomeEntry.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_skill_entry(
        self, db: AsyncSession, user_id: str, skill_id: str
    ) -> SkillGenomeEntry | None:
        """Get a single genome entry for a user + skill."""
        result = await db.execute(
            select(SkillGenomeEntry).where(
                SkillGenomeEntry.user_id == user_id,
                SkillGenomeEntry.ontology_node_id == skill_id,
            )
        )
        return result.scalars().first()

    async def _upsert(
        self,
        db: AsyncSession,
        user_id: str,
        skill_id: str,
        new_signal: float,
        evidence_type: str,
    ) -> SkillGenomeEntry:
        """Upsert a genome entry with EMA mastery update."""
        entry = await self.get_skill_entry(db, user_id, skill_id)

        if entry is None:
            # Resolve skill name + domain from ontology
            ontology = get_ontology_service()
            skill_data = ontology.get_skill(skill_id)
            skill_name = skill_data["name"] if skill_data else skill_id
            domain = skill_data.get("domain") if skill_data else None

            entry = SkillGenomeEntry(
                user_id=user_id,
                ontology_node_id=skill_id,
                skill_name=skill_name,
                domain=domain,
                mastery_level=new_signal,
                evidence_count=1,
                last_evidence=evidence_type,
                confidence=min(1.0, 1 / self.CONFIDENCE_CAP),
            )
            db.add(entry)
        else:
            # EMA update
            entry.mastery_level = (
                self.EMA_WEIGHT * entry.mastery_level
                + (1 - self.EMA_WEIGHT) * new_signal
            )
            # Clamp to 0-4 range
            entry.mastery_level = max(0.0, min(4.0, entry.mastery_level))
            entry.evidence_count += 1
            entry.last_evidence = evidence_type
            entry.confidence = min(1.0, entry.evidence_count / self.CONFIDENCE_CAP)

        await db.flush()
        return entry
