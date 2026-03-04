"""Curiosity Feed service — discovery feed driven by ontology relationships."""
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.skill_genome import SkillGenomeEntry
from app.models.learning_path import LearningPath
from app.services.ontology import OntologyService
from app.services.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)

# Minimum mastery level before a skill "unlocks" dependents
UNLOCK_THRESHOLD = 2.0


class CuriosityFeedService:
    """Generates a discovery feed of skills the learner could explore next."""

    async def generate_feed(
        self,
        db: AsyncSession,
        user_id: str,
        ontology_svc: OntologyService,
        rag: RAGRetriever,
        limit: int = 10,
    ) -> list[dict]:
        """Build a curiosity feed from the user's genome + ontology dependencies.

        Algorithm:
        1. Get user's genome entries with mastery >= UNLOCK_THRESHOLD
        2. For each, find ontology dependents
        3. Filter out skills user already has good mastery on
        4. Rank by relevance and deduplicate
        5. Generate teasers from ontology descriptions
        """
        # 1. Get mastered skills
        result = await db.execute(
            select(SkillGenomeEntry).where(
                SkillGenomeEntry.user_id == user_id,
                SkillGenomeEntry.mastery_level >= UNLOCK_THRESHOLD,
            )
        )
        mastered_entries = result.scalars().all()

        if not mastered_entries:
            return []

        # Build lookup of all user's genome skills for filtering
        all_result = await db.execute(
            select(SkillGenomeEntry).where(SkillGenomeEntry.user_id == user_id)
        )
        all_entries = {e.ontology_node_id: e for e in all_result.scalars().all()}

        # Check which skills user has learning paths for
        path_result = await db.execute(
            select(LearningPath).where(LearningPath.user_id == user_id)
        )
        user_paths = path_result.scalars().all()
        path_skill_ids = set()
        for p in user_paths:
            chapters = p.chapters or []
            if isinstance(chapters, dict):
                chapters = chapters.get("chapters", [])
            for ch in chapters:
                sid = ch.get("skill_id", ch.get("primary_skill_id"))
                if sid:
                    path_skill_ids.add(sid)

        # 2+3. Find dependent skills not yet mastered
        candidates = []
        seen_skill_ids = set()

        for entry in mastered_entries:
            dependents = ontology_svc.get_skill_dependents(entry.ontology_node_id)
            for dep in dependents:
                dep_id = dep["id"]
                if dep_id in seen_skill_ids:
                    continue
                seen_skill_ids.add(dep_id)

                # Skip if user already has strong mastery
                existing = all_entries.get(dep_id)
                if existing and existing.mastery_level >= UNLOCK_THRESHOLD:
                    continue

                # Get domain info
                domain = dep.get("domain")
                domain_data = ontology_svc.get_domain(domain) if domain else None
                domain_label = domain_data.get("label", domain) if domain_data else domain

                # Build teaser from skill description
                teaser = dep.get("description", f"Explore {dep['name']} — builds on your {entry.skill_name} knowledge.")
                if len(teaser) > 200:
                    teaser = teaser[:197] + "..."

                # Relevance: higher mastery of prereq → more relevant
                relevance = min(1.0, entry.mastery_level / 4.0) * entry.confidence

                candidates.append({
                    "skill_id": dep_id,
                    "skill_name": dep["name"],
                    "domain": domain,
                    "domain_label": domain_label,
                    "teaser": teaser,
                    "unlocked_by": entry.skill_name,
                    "relevance_score": round(relevance, 2),
                    "has_learning_path": dep_id in path_skill_ids,
                })

        # 4. Sort by relevance descending
        candidates.sort(key=lambda c: c["relevance_score"], reverse=True)

        return candidates[:limit]
