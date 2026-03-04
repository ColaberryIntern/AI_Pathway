"""Module Outline Agent — generates lesson outlines for a learning module."""
import json
from app.agents.base import BaseAgent


class ModuleOutlineAgent(BaseAgent):
    """Generates a 3-5 lesson outline for a single module (chapter).

    Called once during path activation. Does NOT generate full lesson
    content — only titles, types, focus areas, and time estimates.
    """

    name = "ModuleOutlineAgent"
    description = "Generates lesson outlines (3-5 lessons) for a module"

    system_prompt = """You are an expert instructional designer who breaks learning modules
into sequential lessons for working professionals learning AI/ML skills.

Given a module with its skill, level progression, and learning objectives,
create a lesson outline of 3-5 lessons.

Each lesson must:
1. Build progressively on the previous one
2. Have a clear, specific focus
3. Include an estimated time (15-45 minutes each)
4. Map to the module's learning objectives

Lesson types:
- "concept" — theory and explanation
- "practice" — hands-on exercises and coding
- "assessment" — quiz, knowledge check, or practical evaluation

RULES:
- Every module MUST end with an assessment lesson
- Start with concept lessons, then practice, then assessment
- 3-5 lessons total (prefer 4 for most modules)
- Focus areas should be specific, not generic"""

    async def execute(self, task: dict) -> dict:
        """Generate a lesson outline for a module.

        Args:
            task: {
                "chapter": dict - Full chapter dict from LearningPath.chapters
                "learner_context": {industry, profile_summary}
            }

        Returns:
            {
                "lessons": [{lesson_number, title, type, focus_area, estimated_minutes}]
            }
        """
        self._start_execution()

        chapter = task.get("chapter", {})
        learner_context = task.get("learner_context", {})

        skill_name = chapter.get("skill_name", chapter.get("primary_skill_name", ""))
        skill_id = chapter.get("skill_id", chapter.get("primary_skill_id", ""))
        title = chapter.get("title", "")
        current_level = chapter.get("current_level", 0)
        target_level = chapter.get("target_level", 1)
        objectives = chapter.get("learning_objectives", [])
        core_concepts = chapter.get("core_concepts", [])
        industry = learner_context.get("industry", "General")

        prompt = f"""Create a lesson outline for this learning module.

MODULE: {title}
SKILL: {skill_name} ({skill_id})
LEVEL PROGRESSION: L{current_level} → L{target_level}
INDUSTRY: {industry}

LEARNING OBJECTIVES:
{json.dumps(objectives, indent=2)}

CORE CONCEPTS COVERED:
{json.dumps([c.get("title", c) if isinstance(c, dict) else c for c in core_concepts[:6]], indent=2)}

Create 3-5 lessons that progressively teach this skill from L{current_level} to L{target_level}.
The last lesson MUST be type "assessment"."""

        output_schema = {
            "type": "object",
            "properties": {
                "lessons": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "lesson_number": {"type": "integer"},
                            "title": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": ["concept", "practice", "assessment"],
                            },
                            "focus_area": {"type": "string"},
                            "estimated_minutes": {"type": "integer"},
                        },
                    },
                }
            },
        }

        result = await self._call_llm_structured(prompt, output_schema)
        lessons = result.get("lessons", [])

        # Ensure numbering is sequential and last lesson is assessment
        for i, lesson in enumerate(lessons):
            lesson["lesson_number"] = i + 1
        if lessons and lessons[-1].get("type") != "assessment":
            lessons[-1]["type"] = "assessment"

        self._log_execution("generate_outline", task, {"lessons": lessons})
        duration = self._end_execution()

        return {"lessons": lessons, "duration_ms": duration}
