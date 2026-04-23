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

        # Call LLM with structured output schema
        prompt = f"""Generate a 15-minute interactive chapter for this skill and level gap.

INPUT:
{json.dumps(input_payload, indent=2)}

Generate the chapter content with these 5 sections:
1. scenario (2 min): A realistic situation with A->B level progression, objectives
2. concepts (3 min): 2-4 concept cards with analogies, a mnemonic if natural
3. example_1 (3 min): Applied use case with prompt, output, rating, diagnosis
4. example_2 (4 min): Second use case with A/B comparison of two prompt variants
5. agent_build (3 min): Build a reusable artifact (system prompt template with personalization fields)

Use the rubric_by_level strings to frame the A->B progression.
Make examples specific to the skill domain, not generic.
"""

        output_schema = {
            "type": "object",
            "properties": {
                "meta": {
                    "type": "object",
                    "properties": {
                        "chapter_title": {"type": "string"},
                        "chapter_subtitle": {"type": "string"},
                        "skill_id": {"type": "string"},
                        "skill_name": {"type": "string"},
                        "domain_name": {"type": "string"},
                        "total_minutes": {"type": "integer"},
                    },
                },
                "scenario": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "narrative": {"type": "string"},
                        "a_state": {"type": "object", "properties": {"level_display": {"type": "string"}, "quote": {"type": "string"}}},
                        "b_state": {"type": "object", "properties": {"level_display": {"type": "string"}, "quote": {"type": "string"}}},
                        "objectives": {"type": "array", "items": {"type": "string"}},
                        "why_it_matters": {"type": "string"},
                    },
                },
                "concepts": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "intro": {"type": "string"},
                        "mnemonic": {"type": "string"},
                        "cards": {"type": "array", "items": {
                            "type": "object",
                            "properties": {
                                "identifier": {"type": "string"},
                                "word": {"type": "string"},
                                "headline": {"type": "string"},
                                "body": {"type": "string"},
                                "analogy": {"type": "string"},
                            },
                        }},
                        "pull_quote": {"type": "string"},
                    },
                },
                "example_1": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "setup": {"type": "string"},
                        "original_prompt": {"type": "object", "properties": {
                            "label": {"type": "string"}, "prompt": {"type": "string"},
                            "output": {"type": "string"}, "rating": {"type": "integer"},
                            "diagnosis": {"type": "string"},
                        }},
                        "iterated_prompt": {"type": "object", "properties": {
                            "label": {"type": "string"}, "prompt": {"type": "string"},
                            "output": {"type": "string"}, "rating": {"type": "integer"},
                            "diagnosis": {"type": "string"},
                        }},
                    },
                },
                "example_2": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "setup": {"type": "string"},
                        "comparison": {"type": "object", "properties": {
                            "test_question": {"type": "string"},
                            "variants": {"type": "array", "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"}, "label": {"type": "string"},
                                    "prompt": {"type": "string"}, "output": {"type": "string"},
                                    "rating": {"type": "integer"}, "why": {"type": "string"},
                                },
                            }},
                            "takeaway": {"type": "string"},
                        }},
                    },
                },
                "agent_build": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "intro": {"type": "string"},
                        "capability_chips": {"type": "array", "items": {
                            "type": "object",
                            "properties": {"title": {"type": "string"}, "description": {"type": "string"}},
                        }},
                        "personalization_fields": {"type": "array", "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string"}, "label": {"type": "string"},
                                "placeholder": {"type": "string"}, "input_type": {"type": "string"},
                            },
                        }},
                        "system_prompt_template": {"type": "string"},
                        "usage_steps": {"type": "array", "items": {"type": "string"}},
                        "final_affirmation": {"type": "object", "properties": {
                            "rubric_quote": {"type": "string"}, "tie_back": {"type": "string"},
                        }},
                    },
                },
            },
            "required": ["meta", "scenario", "concepts", "example_1", "example_2", "agent_build"],
        }

        chapter_spec = await self._call_llm_structured(prompt, output_schema, temperature=0.7)

        # Normalize: LLM may use slightly different keys
        # Handle "examples" array instead of "example_1"/"example_2"
        if "examples" in chapter_spec and "example_1" not in chapter_spec:
            examples = chapter_spec.pop("examples", [])
            if isinstance(examples, list):
                if len(examples) >= 1:
                    chapter_spec["example_1"] = examples[0]
                if len(examples) >= 2:
                    chapter_spec["example_2"] = examples[1]
            elif isinstance(examples, dict):
                chapter_spec["example_1"] = examples

        # Handle "objectives" at top level (should be inside scenario)
        if "objectives" in chapter_spec and "scenario" in chapter_spec:
            scenario = chapter_spec["scenario"]
            if isinstance(scenario, dict) and "objectives" not in scenario:
                scenario["objectives"] = chapter_spec.pop("objectives")
            else:
                chapter_spec.pop("objectives", None)

        # Validate required sections
        required = ["meta", "scenario", "concepts", "agent_build"]
        optional = ["example_1", "example_2"]
        missing = [s for s in required if s not in chapter_spec]
        if missing:
            logger.warning("ChapterSpec missing required sections: %s", missing)
        missing_opt = [s for s in optional if s not in chapter_spec]
        if missing_opt:
            logger.info("ChapterSpec missing optional sections (will use defaults): %s", missing_opt)

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
