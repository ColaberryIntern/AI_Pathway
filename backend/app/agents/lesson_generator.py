"""Lesson Generator Agent — generates full lesson content on-demand."""
import json
from app.agents.base import BaseAgent


class LessonGeneratorAgent(BaseAgent):
    """Generates full lesson content when a learner starts a lesson.

    Content is generated once and cached in the database.
    Generates: explanation, code examples, exercises, knowledge checks,
    and hands-on tasks.
    """

    name = "LessonGeneratorAgent"
    description = "Generates full lesson content on-demand when a learner starts a lesson"

    system_prompt = """You are an expert instructional designer creating interactive,
hands-on lessons for working professionals learning AI/ML skills.

Each lesson must include:
1. EXPLANATION — Clear, progressive explanation of the topic (500-1000 words).
   Use analogies from the learner's industry when possible.
2. CODE_EXAMPLES — 2-3 runnable code examples with inline comments explaining each step.
3. EXERCISES — 1-2 practice exercises with clear instructions, starter code, and expected outputs.
4. KNOWLEDGE_CHECKS — 3-5 quiz questions (multiple choice). Include the correct answer and
   a brief explanation for each option.
5. HANDS_ON_TASKS — 1 practical task the learner builds from scratch.

RULES:
- Content must match the skill level progression (current_level → target_level)
- Code examples must be complete and runnable (Python unless otherwise specified)
- Exercises must have clear deliverables and hints for if the learner gets stuck
- Knowledge checks must test understanding, not memorization
- Adapt complexity to the lesson's position in the module sequence
- Keep language professional but approachable — like a supportive senior colleague
- For concept lessons: emphasize explanation and knowledge checks
- For practice lessons: emphasize code examples, exercises, and hands-on tasks
- For assessment lessons: emphasize knowledge checks and a comprehensive hands-on task"""

    async def execute(self, task: dict) -> dict:
        """Generate full lesson content.

        Args:
            task: {
                "module": {skill_id, skill_name, title, current_level, target_level},
                "lesson_number": int,
                "lesson_title": str,
                "lesson_type": "standard" | "concept" | "practice" | "assessment" | "reinforcement",
                "lesson_focus_area": str,
                "learner_context": {industry, profile_summary, previous_quiz_scores},
                "module_context": {total_lessons, lesson_outline, preceding_lesson_titles}
            }

        Returns:
            {
                "content": {
                    "explanation": str,
                    "code_examples": [{title, language, code, explanation}],
                    "exercises": [{id, title, instructions, starter_code, expected_output, hints[], estimated_minutes}],
                    "knowledge_checks": [{question, options[], correct_answer, explanation}],
                    "hands_on_tasks": [{title, description, requirements[], deliverable, estimated_minutes}]
                }
            }
        """
        self._start_execution()

        module = task.get("module", {})
        lesson_number = task.get("lesson_number", 1)
        lesson_title = task.get("lesson_title", "")
        lesson_type = task.get("lesson_type", "standard")
        lesson_focus = task.get("lesson_focus_area", "")
        learner_ctx = task.get("learner_context", {})
        module_ctx = task.get("module_context", {})

        preceding = module_ctx.get("preceding_lesson_titles", [])
        preceding_str = "\n".join(f"  - {t}" for t in preceding) if preceding else "  (This is the first lesson)"

        prompt = f"""Generate a full lesson for a working professional learning AI/ML skills.

MODULE: {module.get('title', '')}
SKILL: {module.get('skill_name', '')} ({module.get('skill_id', '')})
LEVEL: L{module.get('current_level', 0)} → L{module.get('target_level', 1)}

LESSON: #{lesson_number} — {lesson_title}
TYPE: {lesson_type}
FOCUS: {lesson_focus}
INDUSTRY: {learner_ctx.get('industry', 'General')}

CONTEXT:
- Total lessons in this module: {module_ctx.get('total_lessons', 4)}
- Preceding lessons:
{preceding_str}

Generate the lesson content. Ensure it builds on what the learner has already covered
and matches the "{lesson_type}" lesson type."""

        output_schema = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "object",
                    "properties": {
                        "explanation": {"type": "string"},
                        "code_examples": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "language": {"type": "string"},
                                    "code": {"type": "string"},
                                    "explanation": {"type": "string"},
                                },
                            },
                        },
                        "exercises": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "instructions": {"type": "string"},
                                    "starter_code": {"type": "string"},
                                    "expected_output": {"type": "string"},
                                    "hints": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "estimated_minutes": {"type": "integer"},
                                },
                            },
                        },
                        "knowledge_checks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "options": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "correct_answer": {"type": "string"},
                                    "explanation": {"type": "string"},
                                },
                            },
                        },
                        "hands_on_tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "requirements": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "deliverable": {"type": "string"},
                                    "estimated_minutes": {"type": "integer"},
                                },
                            },
                        },
                    },
                }
            },
        }

        result = await self._call_llm_structured(
            prompt, output_schema, max_tokens=16384
        )

        content = result.get("content", {})

        # Ensure all required sections exist (fallback to empty lists)
        content.setdefault("explanation", "")
        content.setdefault("code_examples", [])
        content.setdefault("exercises", [])
        content.setdefault("knowledge_checks", [])
        content.setdefault("hands_on_tasks", [])

        self._log_execution("generate_lesson", task, {"content_keys": list(content.keys())})
        duration = self._end_execution()

        return {"content": content, "duration_ms": duration}
