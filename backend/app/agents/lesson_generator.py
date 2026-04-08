"""Lesson Generator Agent — generates full lesson content on-demand."""
import json
import logging
from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


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

4. CODE_EXAMPLES or TOOL_WALKTHROUGH — Depends on the learner's technical background:
   - If the learner is technical (has coding experience): Provide 2-3 runnable code examples
     with comments explaining each step.
   - If the learner is NON-TECHNICAL (no coding experience): Instead of code, provide a
     TOOL_WALKTHROUGH — a step-by-step guide using no-code/low-code tools, AI assistants
     (ChatGPT, Claude, Copilot), spreadsheets, or visual platforms. Walk through the exact
     clicks, prompts, and settings. NEVER show raw Python or code to non-technical learners.

5. IMPLEMENTATION_TASK — A hands-on task where the learner builds something real.
   - For technical learners: Must require code/deliverable + brief architecture explanation.
   - For non-technical learners: Must be a PROMPT_PRACTICE or TOOL_EXERCISE using AI tools,
     spreadsheets, or visual platforms. Focus on using AI to accomplish the goal, not coding.
   Include requirements list, deliverable description, estimated minutes.
   Include a "tools" array listing each tool, API, or platform needed.
   Each tool must include: name, url (tool homepage), is_free (boolean).
   Mark free/open-source tools as is_free=true, paid/commercial tools as is_free=false.
   Include an "evidence_requirements" array describing what proof the learner must submit.
   Each evidence item needs: name (short label), description (what to submit), format ("screenshot"|"file"|"code").
   Always require proof that demonstrates the output is correct — e.g., screenshots of
   successful execution output, API responses with status 200, SSIS packages showing success,
   terminal output showing expected results. Do NOT just ask for "a script" — ask for the
   script AND a screenshot proving it ran correctly.

   CRITICAL - DATA AND FILES:
   If the task requires ANY input data (CSV, JSON, logs, patient records, transaction data,
   etc.), you MUST do ONE of the following:
   a) Include the complete sample data INLINE in the task description as a formatted table,
      CSV block, or JSON block. The learner should be able to copy-paste it directly.
   b) Provide an exact prompt the learner can paste into ChatGPT/Claude to GENERATE the
      sample data themselves. Write the prompt for them - do not assume they know how.
   c) Use only data the learner can create themselves in 2 minutes (e.g., "Open a new
      Google Sheet and enter 10 rows of...").
   NEVER say "use a dataset" or "access logs" without providing them. The learner has
   NOTHING except this lesson, a web browser, and free AI tools. If they cannot complete
   the task with what you provide, the task is broken.

6. REFLECTION_QUESTIONS — 3-4 questions that force metacognition about AI usage.
   Each question MUST reference the specific implementation task from section 5.
   Do NOT ask generic metacognition questions unrelated to this lesson's content.
   Ask about: How did your prompt evolve during THIS task? What did AI get wrong
   on THIS specific deliverable? What would you NOT delegate to AI for THIS use case?
   Each question's prompt_for_deeper_thinking MUST be a detailed, context-rich prompt
   (at least 30 words) that references the specific skill, lesson topic, and a concrete
   scenario. Example: "Ask the AI: 'As a data analyst working with sales data, explain
   how the prompt engineering technique of role-playing would change the quality of
   insights you get compared to generic prompting, with 2 specific examples.'"

7. KNOWLEDGE_CHECKS — Exactly 5 quiz questions testing understanding.
   CRITICAL: Every question MUST be answerable solely from the CONCEPT_SNAPSHOT and
   AI_STRATEGY sections above. Do NOT ask about topics, tools, frameworks, or concepts
   not explicitly covered in this lesson. If you taught about stakeholder identification,
   only ask about stakeholder identification — not about legal compliance or other topics.
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
- implementation_task must require code AND may optionally include an architecture explanation.
- Code examples must be complete and runnable (Python unless otherwise specified).
- Python code examples MUST only use standard library modules plus: numpy, pandas, scikit-learn, matplotlib, scipy, sympy, regex. Do NOT use transformers, torch, tensorflow, openai, langchain, or any package requiring native compilation or network access. Code runs in a browser sandbox (Pyodide/WebAssembly).
- Adapt complexity to the lesson's position in the module sequence.
- Use analogies from the learner's industry when possible.
- For concept lessons: emphasize concept_snapshot, ai_strategy, knowledge_checks.
- For practice lessons: emphasize prompt_template, code_examples, implementation_task.
- For assessment lessons: emphasize knowledge_checks and a comprehensive implementation_task.
- If any exercise, code example, or implementation task references input files (CSV, JSON, Excel, etc.),
  you MUST generate realistic sample data INLINE as a formatted table, JSON block, or CSV block within
  the lesson content. NEVER reference files the learner does not have access to. The learner should be
  able to complete every exercise with only what is provided in the lesson."""

    @staticmethod
    def _extract_from_schema_echo(schema: dict) -> dict:
        """Extract actual content from a schema-echo LLM response.

        When the LLM returns the JSON schema definition back (with content
        embedded in 'description' fields), this extracts the real values.
        """
        content = {}
        props = schema.get("properties", {})
        # Unwrap "content" wrapper if present
        if "content" in props and "properties" in props["content"]:
            props = props["content"]["properties"]

        for key, val in props.items():
            if isinstance(val, dict):
                if val.get("type") == "string" and "description" in val:
                    content[key] = val["description"]
                elif val.get("type") == "object" and "properties" in val:
                    # Recurse one level for nested objects like ai_strategy
                    inner = {}
                    for ik, iv in val["properties"].items():
                        if isinstance(iv, dict) and "description" in iv:
                            inner[ik] = iv["description"]
                    content[key] = inner if inner else {}
                elif val.get("type") == "array":
                    content[key] = []  # Can't reliably extract arrays
                else:
                    content[key] = {}
        return content

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
                "content": {concept_snapshot, ai_strategy, prompt_template, ...},
                "duration_ms": int
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

        industry = learner_ctx.get('industry', 'General')
        target_role = learner_ctx.get('target_role', '')
        profile_summary = learner_ctx.get('profile_summary', '')
        technical_background = learner_ctx.get('technical_background', '')

        # Determine if learner is non-technical
        is_non_technical = technical_background.lower() in (
            'no coding experience', 'no technical background', 'non-technical', ''
        ) if technical_background else True  # Default to non-technical if unknown

        role_section = ""
        if target_role:
            role_section = f"\nTARGET ROLE: {target_role}"
        if profile_summary:
            role_section += f"\nLEARNER BACKGROUND: {profile_summary[:300]}"

        tech_level_section = ""
        if is_non_technical:
            tech_level_section = """
TECHNICAL LEVEL: NON-TECHNICAL
The learner has NO coding experience. You MUST:
- Replace all CODE_EXAMPLES with TOOL_WALKTHROUGH (step-by-step guides using AI tools, spreadsheets, or visual platforms)
- Replace code-based IMPLEMENTATION_TASK with PROMPT_PRACTICE or TOOL_EXERCISE
- NEVER show raw Python, JavaScript, or any programming code
- Use ChatGPT/Claude prompts, Google Sheets formulas, or no-code tool instructions instead
- Focus on what buttons to click, what prompts to write, what settings to configure"""
        else:
            tech_level_section = f"\nTECHNICAL LEVEL: {technical_background} (include code examples as appropriate)"

        prompt = f"""Generate a full AI-native lesson for a working professional.

MODULE: {module.get('title', '')}
SKILL: {module.get('skill_name', '')} ({module.get('skill_id', '')})
LEVEL: L{module.get('current_level', 0)} -> L{module.get('target_level', 1)}

LESSON: #{lesson_number} -- {lesson_title}
TYPE: {lesson_type}
FOCUS: {lesson_focus}
INDUSTRY: {industry}{role_section}{tech_level_section}

CONTEXT:
- Total lessons in this module: {module_ctx.get('total_lessons', 4)}
- Preceding lessons:
{preceding_str}

INDUSTRY-SPECIFIC REQUIREMENT:
All exercises, code examples, implementation tasks, and prompt templates MUST use
realistic scenarios from the {industry} industry{f' and the {target_role} role' if target_role else ''}.
Do NOT use generic examples. The learner should recognize these as tasks they would
actually encounter in their target position. For example:
- If the industry is "Marketing & Creative" and the role is "AI Content Editor",
  use content editing, brand voice, editorial workflow scenarios.
- If the industry is "Healthcare", use clinical data, patient records, compliance scenarios.
- If the industry is "Education", use curriculum design, training delivery, learner assessment scenarios.

Generate the lesson content. The learner should leave this lesson knowing how to USE AI
to work with this concept, not just understand it theoretically.
Ensure it builds on what the learner has already covered
and matches the "{lesson_type}" lesson type."""

        # Flat schema — no "content" wrapper. Reduces nesting and prevents
        # the LLM from echoing back the schema definition instead of data.
        output_schema = {
            "type": "object",
            "properties": {
                "concept_snapshot": {"type": "string"},
                "ai_strategy": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "when_to_use_ai": {"type": "array", "items": {"type": "string"}},
                        "human_responsibilities": {"type": "array", "items": {"type": "string"}},
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
                        "requirements": {"type": "array", "items": {"type": "string"}},
                        "deliverable": {"type": "string"},
                        "requires_architecture_explanation": {"type": "boolean"},
                        "estimated_minutes": {"type": "integer"},
                        "tools": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "url": {"type": "string"},
                                    "is_free": {"type": "boolean"},
                                },
                            },
                        },
                        "evidence_requirements": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "format": {"type": "string"},
                                },
                            },
                        },
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
                "knowledge_checks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "options": {"type": "array", "items": {"type": "string"}},
                            "correct_answer": {"type": "string"},
                            "explanation": {"type": "string"},
                            "ai_followup_prompt": {"type": "string"},
                        },
                    },
                },
                "exercises": {"type": "array", "items": {"type": "object"}},
                "hands_on_tasks": {"type": "array", "items": {"type": "object"}},
            },
        }

        result = await self._call_llm_structured(
            prompt, output_schema, max_tokens=16384
        )

        # Extract content — the flat schema returns fields directly at top level.
        # Also handle legacy "content" wrapper and schema-echo responses.
        _content_keys = {"concept_snapshot", "ai_strategy", "prompt_template",
                         "explanation", "knowledge_checks"}

        if any(isinstance(result.get(k), str) and result.get(k) for k in _content_keys):
            # Normal case: content fields at top level with string values
            content = result
        elif isinstance(result.get("content"), dict):
            # Legacy: content nested under "content" key
            content = result["content"]
            logger.info("LLM returned content under 'content' wrapper key")
        elif "properties" in result:
            # Schema-echo: LLM returned the schema definition with content in
            # description fields. Extract actual values from the schema structure.
            logger.warning("LLM echoed schema — extracting content from 'description' fields")
            content = self._extract_from_schema_echo(result)
        else:
            content = result

        logger.info(
            "LLM result extraction: result_keys=%s, content_type=%s",
            list(result.keys())[:5], type(content).__name__,
        )

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

        logger.info(
            "Lesson generator result: content_keys=%s, snapshot_len=%d, kc_count=%d",
            list(content.keys()),
            len(content.get("concept_snapshot", "") or ""),
            len(content.get("knowledge_checks", []) or []),
        )

        self._log_execution("generate_lesson", task, {"content_keys": list(content.keys())})
        duration = self._end_execution()

        return {"content": content, "duration_ms": duration}
