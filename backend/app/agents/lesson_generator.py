"""Lesson Generator Agent — generates full lesson content on-demand."""
import json
from app.agents.base import BaseAgent


class LessonGeneratorAgent(BaseAgent):
    """Generates full lesson content when a learner starts a lesson.

    Content is generated once and cached in the database.
    Produces AI-native lesson format: concept snapshot, AI strategy,
    prompt template, implementation task, reflection, and quiz.
    Legacy fields (explanation, exercises, hands_on_tasks) are preserved
    for backward compatibility with older cached lessons.
    """

    name = "LessonGeneratorAgent"
    description = "Generates full lesson content on-demand when a learner starts a lesson"

    system_prompt = """You are an expert AI-native instructional designer creating lessons
that teach working professionals how to USE AI as a core skill — not just learn about it.

Each lesson must include these sections:

1. CONCEPT_SNAPSHOT — Maximum 4 sentences. Crisp, precise explanation of the core concept.
   No filler, no preamble. Like a brilliant colleague giving a 30-second brief.

2. AI_STRATEGY — How to use AI (LLMs, agents, tools) to solve problems in this topic area.
   Include: when to use AI, what to delegate to AI, what humans must still own.
   Include a suggested prompt the learner can try.

3. PROMPT_TEMPLATE — A ready-to-use prompt the learner can copy and customize.
   Include {{placeholders}} the learner fills in. Describe each placeholder.
   Include the expected shape of the AI output.

4. CODE_EXAMPLES — 2-3 runnable code examples with comments explaining each step.

5. IMPLEMENTATION_TASK — A hands-on task where the learner builds something real.
   Must require: code/deliverable + prompt history + brief architecture explanation.
   Include requirements list, deliverable description, estimated minutes.

6. REFLECTION_QUESTIONS — 3-4 questions that force metacognition about AI usage:
   How did your prompt evolve? What did AI get wrong? What did you improve?
   What would you NOT delegate to AI? Why?
   Each question's prompt_for_deeper_thinking MUST be a detailed, context-rich prompt
   (at least 30 words) that references the specific skill, lesson topic, and a concrete
   scenario. Example: "Ask the AI: 'As a data analyst working with sales data, explain
   how the prompt engineering technique of role-playing would change the quality of
   insights you get compared to generic prompting, with 2 specific examples.'"

7. KNOWLEDGE_CHECKS — 3-5 quiz questions testing understanding.
   Each question's ai_followup_prompt MUST be a detailed, self-contained question
   (at least 30 words) that gives the AI Mentor enough context to provide targeted help.
   Include: the specific concept being tested, what the learner should explore, and a
   concrete angle or constraint. Example: "Explain why choosing an open-source AI model
   for healthcare data analysis requires different compliance considerations than a
   proprietary model, covering HIPAA, data residency, and audit trail requirements."

8. EXPLANATION — A brief summary (2-3 paragraphs) for reference. This is secondary
   to the concept snapshot — keep it concise.

RULES:
- concept_snapshot is THE primary learning content. 4 sentences max. Make them count.
- ai_strategy must be practical and specific to this skill, not generic AI advice.
- prompt_template must be copy-pasteable with clear {{placeholders}}.
- implementation_task must require BOTH code AND prompt strategy documentation.
- Code examples must be complete and runnable (Python unless otherwise specified).
- Adapt complexity to the lesson's position in the module sequence.
- Use analogies from the learner's industry when possible.
- For concept lessons: emphasize concept_snapshot, ai_strategy, knowledge_checks.
- For practice lessons: emphasize prompt_template, code_examples, implementation_task.
- For assessment lessons: emphasize knowledge_checks and a comprehensive implementation_task."""

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
                    "concept_snapshot": str,
                    "ai_strategy": {description, when_to_use_ai[], human_responsibilities[], suggested_prompt},
                    "prompt_template": {template, placeholders[], expected_output_shape},
                    "code_examples": [{title, language, code, explanation}],
                    "implementation_task": {title, description, requirements[], deliverable, ...},
                    "reflection_questions": [{question, prompt_for_deeper_thinking}],
                    "knowledge_checks": [{question, options[], correct_answer, explanation, ai_followup_prompt}],
                    "explanation": str,
                    "exercises": [...],
                    "hands_on_tasks": [...]
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

        prompt = f"""Generate a full AI-native lesson for a working professional.

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

Generate the lesson content. The learner should leave this lesson knowing how to USE AI
to work with this concept, not just understand it theoretically.
Ensure it builds on what the learner has already covered
and matches the "{lesson_type}" lesson type."""

        output_schema = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "object",
                    "properties": {
                        # --- NEW AI-native sections ---
                        "concept_snapshot": {"type": "string"},
                        "ai_strategy": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "when_to_use_ai": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "human_responsibilities": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "suggested_prompt": {"type": "string"},
                            },
                        },
                        "prompt_template": {
                            "type": "object",
                            "properties": {
                                "template": {"type": "string"},
                                "placeholders": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "description": {"type": "string"},
                                            "example": {"type": "string"},
                                        },
                                    },
                                },
                                "expected_output_shape": {"type": "string"},
                            },
                        },
                        "implementation_task": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "requirements": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "deliverable": {"type": "string"},
                                "requires_prompt_history": {"type": "boolean"},
                                "requires_architecture_explanation": {"type": "boolean"},
                                "estimated_minutes": {"type": "integer"},
                            },
                        },
                        "reflection_questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "prompt_for_deeper_thinking": {"type": "string"},
                                },
                            },
                        },
                        # --- PRESERVED sections (backward compat) ---
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
                                    "ai_followup_prompt": {"type": "string"},
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

        # Ensure all sections exist with defaults
        # New AI-native sections
        content.setdefault("concept_snapshot", "")
        content.setdefault("ai_strategy", {})
        content.setdefault("prompt_template", {})
        content.setdefault("implementation_task", {})
        content.setdefault("reflection_questions", [])
        # Legacy sections (backward compat)
        content.setdefault("explanation", "")
        content.setdefault("code_examples", [])
        content.setdefault("exercises", [])
        content.setdefault("knowledge_checks", [])
        content.setdefault("hands_on_tasks", [])

        self._log_execution("generate_lesson", task, {"content_keys": list(content.keys())})
        duration = self._end_execution()

        return {"content": content, "duration_ms": duration}
