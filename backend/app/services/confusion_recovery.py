"""Confusion Recovery service — generates alternative explanations when a learner is confused."""
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.confusion_event import ConfusionEvent
from app.models.lesson import Lesson
from app.models.module import Module
from app.services.llm.base import BaseLLMProvider
from app.services.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)

RECOVERY_SYSTEM_PROMPT = """You are an expert learning recovery specialist.
A learner is confused about a concept and needs an alternative explanation.
Your job is to explain the same concept in a completely different way than the original lesson.

Respond with VALID JSON matching this exact schema:
{
    "analogy": "A relatable real-world analogy that makes the concept click",
    "step_by_step": ["Step 1...", "Step 2...", "Step 3..."],
    "real_world_example": "A concrete example from industry/daily life",
    "common_misconceptions": ["Misconception 1...", "Misconception 2..."],
    "suggested_mentor_prompt": "A question the learner can ask the AI Mentor to go deeper"
}

Guidelines:
- Use simple, everyday language
- The analogy should be from a completely different domain
- Step-by-step should break down the concept into tiny, digestible pieces
- Include 2-3 common misconceptions
- Keep total response under 500 words
- Return ONLY valid JSON, no markdown or extra text"""


class ConfusionRecoveryService:
    """Generates alternative explanations using LLM + RAG."""

    async def generate_recovery(
        self,
        db: AsyncSession,
        llm: BaseLLMProvider,
        rag: RAGRetriever,
        lesson: Lesson,
        section: str,
        user_id: str,
    ) -> dict:
        """Generate recovery content for a confused learner."""
        # Get module for skill context
        module = await db.get(Module, lesson.module_id)
        skill_id = module.skill_id if module else None
        skill_name = module.skill_name if module else "Unknown"

        # Try to get alternative content from RAG
        rag_context = ""
        if skill_id:
            try:
                rag_results = rag.retrieve_learning_content(skill_id)
                if rag_results:
                    rag_context = "\n".join(
                        r.get("content", "")[:300] for r in rag_results[:3]
                    )
            except Exception as e:
                logger.warning("RAG retrieval failed (non-blocking): %s", e)

        # Extract the section content from the lesson
        content = lesson.content or {}
        section_content = ""
        if section == "concept_snapshot":
            section_content = content.get("concept_snapshot", "")
        elif section == "ai_strategy":
            strategy = content.get("ai_strategy", {})
            section_content = strategy.get("description", "") if isinstance(strategy, dict) else str(strategy)
        elif section == "explanation":
            section_content = content.get("explanation", "")
        else:
            # Combine key sections for general confusion
            section_content = content.get("concept_snapshot", "") or content.get("explanation", "")

        prompt = f"""SKILL: {skill_name}
SECTION: {section}

ORIGINAL EXPLANATION (what confused the learner):
{section_content[:1000]}

{f"ADDITIONAL CONTEXT FROM KNOWLEDGE BASE:{chr(10)}{rag_context}" if rag_context else ""}

Please provide an alternative explanation using a different approach, analogy, and structure."""

        try:
            llm_response = await llm.generate(
                prompt=prompt,
                system_prompt=RECOVERY_SYSTEM_PROMPT,
                max_tokens=1024,
                temperature=0.7,
                json_mode=True,
            )
            recovery = json.loads(llm_response.content)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Recovery generation failed, using fallback: %s", e)
            recovery = {
                "analogy": f"Think of {skill_name} like learning to ride a bike — you need to practice the basics before tackling advanced moves.",
                "step_by_step": [
                    f"First, understand the core idea behind {skill_name}",
                    "Try re-reading the concept snapshot slowly",
                    "Ask the AI Mentor to explain it in simpler terms",
                ],
                "real_world_example": f"In everyday work, {skill_name} helps you be more effective by automating repetitive tasks.",
                "common_misconceptions": [
                    "You don't need to memorize everything — understanding the principle is enough",
                    "It's normal to feel confused the first time — mastery comes with practice",
                ],
                "suggested_mentor_prompt": f"Can you explain {skill_name} using a simple everyday example?",
            }

        # Save confusion event
        event = ConfusionEvent(
            user_id=user_id,
            lesson_id=lesson.id,
            skill_id=skill_id,
            section=section,
            recovery_content=recovery,
        )
        db.add(event)
        await db.flush()

        return recovery
