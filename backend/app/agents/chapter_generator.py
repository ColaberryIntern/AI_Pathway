"""Chapter Generator Agent — Generates 15-minute interactive chapters
using Vivek's chapter format (5 sections: scenario, concepts, example_1,
example_2, agent_build).

Each chapter teaches exactly one level gap for one skill.
Output is a ChapterSpec JSON object.
"""
import json
import logging
import os
from pathlib import Path

from app.agents.base import BaseAgent
from app.services.ontology import get_ontology_service

logger = logging.getLogger(__name__)

# Load the chapter generator prompt
_PROMPT_PATH = Path(__file__).parent.parent / "data" / "chapter-generator-prompt.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8") if _PROMPT_PATH.exists() else ""

# Level labels matching Vivek's ontology
LEVEL_LABELS = ["Unaware", "Awareness", "Literacy", "Practitioner", "Expert", "Architect"]


class ChapterGeneratorAgent(BaseAgent):
    """Agent for generating 15-minute interactive chapters."""

    name = "ChapterGeneratorAgent"
    description = "Generates personalized 15-minute chapters for one skill level gap"

    system_prompt = _SYSTEM_PROMPT

    async def execute(self, task: dict) -> dict:
        """Generate a chapter for a skill level gap.

        Args:
            task: {
                "skill_id": str - Ontology skill ID (e.g., SK.PRM.003)
                "current_level": int - Learner's current level (0-4)
                "target_level": int - Target level (1-5, must be current+1)
                "learner_context": dict - Optional learner info (industry, role, etc.)
            }

        Returns:
            {
                "content": dict - ChapterSpec JSON object
                "duration_ms": int
            }
        """
        self._start_execution()

        skill_id = task.get("skill_id", "")
        current_level = task.get("current_level", 0)
        target_level = task.get("target_level", current_level + 1)
        learner_ctx = task.get("learner_context", {})

        # Get skill data with rubrics from ontology
        ontology = get_ontology_service()
        skill_data = ontology.get_skill_for_chapter(skill_id)

        if not skill_data:
            raise ValueError(f"Skill {skill_id} not found in ontology")

        rubrics = skill_data.get("rubric_by_level", [])
        if len(rubrics) < 6:
            logger.warning("Skill %s has incomplete rubric data (%d levels)", skill_id, len(rubrics))
            # Pad with generic descriptions
            while len(rubrics) < 6:
                rubrics.append(f"Level {len(rubrics)} proficiency")

        # Build the input payload matching Vivek's contract
        input_payload = {
            "skill": {
                "id": skill_data["id"],
                "name": skill_data["name"],
                "domain_id": skill_data["domain_id"],
                "domain_name": skill_data["domain_name"],
                "rubric_by_level": rubrics,
            },
            "current_level": current_level,
            "target_level": target_level,
        }

        # Add learner context if available (for personalization)
        if learner_ctx:
            input_payload["learner"] = {
                "industry": learner_ctx.get("industry", "General"),
                "role": learner_ctx.get("target_role", ""),
                "technical_background": learner_ctx.get("technical_background", ""),
            }

        # Call LLM with the chapter generator prompt
        prompt = json.dumps(input_payload, indent=2)

        response = await self._call_llm(
            prompt=prompt,
            temperature=0.7,  # Creative content needs some temperature
        )

        # _call_llm returns content string directly
        content_text = response if isinstance(response, str) else str(response)

        # Try to extract JSON from fenced code block
        chapter_spec = None

        # Method 1: Look for ```json ... ``` block
        import re
        json_match = re.search(r'```json\s*([\s\S]*?)```', content_text)
        if json_match:
            try:
                chapter_spec = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from fenced block")

        # Method 2: Try parsing the entire response as JSON
        if not chapter_spec:
            try:
                chapter_spec = json.loads(content_text)
            except json.JSONDecodeError:
                pass

        # Method 3: Find the first { ... } block
        if not chapter_spec:
            brace_start = content_text.find('{')
            if brace_start >= 0:
                # Find matching closing brace
                depth = 0
                for i in range(brace_start, len(content_text)):
                    if content_text[i] == '{':
                        depth += 1
                    elif content_text[i] == '}':
                        depth -= 1
                        if depth == 0:
                            try:
                                chapter_spec = json.loads(content_text[brace_start:i+1])
                            except json.JSONDecodeError:
                                pass
                            break

        if not chapter_spec:
            raise ValueError("Failed to extract ChapterSpec JSON from LLM response")

        # Validate required sections
        required = ["meta", "scenario", "concepts", "example_1", "example_2", "agent_build"]
        missing = [s for s in required if s not in chapter_spec]
        if missing:
            logger.warning("ChapterSpec missing sections: %s", missing)

        # Ensure meta has correct skill info
        if "meta" in chapter_spec:
            meta = chapter_spec["meta"]
            meta.setdefault("skill_id", skill_id)
            meta.setdefault("skill_name", skill_data["name"])
            meta.setdefault("domain_id", skill_data["domain_id"])
            meta.setdefault("domain_name", skill_data["domain_name"])
            meta.setdefault("current_level", current_level)
            meta.setdefault("target_level", target_level)
            meta.setdefault("current_level_label", LEVEL_LABELS[current_level] if current_level < len(LEVEL_LABELS) else "Unknown")
            meta.setdefault("target_level_label", LEVEL_LABELS[target_level] if target_level < len(LEVEL_LABELS) else "Unknown")
            meta.setdefault("current_level_rubric", rubrics[current_level] if current_level < len(rubrics) else "")
            meta.setdefault("target_level_rubric", rubrics[target_level] if target_level < len(rubrics) else "")
            meta.setdefault("total_minutes", 15)

        self._log_execution("generate_chapter", {"skill_id": skill_id, "level_gap": f"L{current_level}->L{target_level}"}, {"sections": list(chapter_spec.keys())})
        result_duration = self._end_execution()

        return {
            "content": chapter_spec,
            "duration_ms": result_duration,
        }
