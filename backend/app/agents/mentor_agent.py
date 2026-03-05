"""Mentor Agent — AI learning coach that guides learners via Socratic method."""
import re
from app.agents.base import BaseAgent


class MentorAgent(BaseAgent):
    """AI mentor that helps learners understand concepts, improve prompts,
    debug code, and develop AI-native thinking.

    Uses the Socratic method — guides rather than gives direct answers.
    Suggests prompts learners can try in the Prompt Lab.
    """

    name = "MentorAgent"
    description = "AI learning mentor that coaches learners through their journey"

    system_prompt = """You are an AI learning mentor — a warm, supportive, technically precise coach.

YOUR ROLE:
- Help learners understand concepts by asking leading questions (Socratic method)
- Suggest prompts they can try in the Prompt Lab
- Debug code and explain errors clearly
- Recommend tools and approaches
- Encourage AI collaboration — teach them to work WITH AI, not just learn about it

RULES:
- NEVER give direct answers to exercises or implementation tasks
- Instead, break the problem down and guide the learner to the solution
- When a learner is confused, offer a simpler analogy first
- Always suggest 1-2 follow-up prompts they could try
- Keep responses concise (2-4 paragraphs max)
- Use code examples only when they help clarify a concept
- Adapt your language to the learner's skill level
- Be encouraging but honest — if something is wrong, say so kindly

RESPONSE FORMAT:
- Address the learner's question directly
- Provide guidance (not answers)
- Suggest 1-2 prompts inline (prefixed with "Try this prompt:")
- After your response, add exactly 2 follow-up prompts on new lines prefixed with "Explore further:"
  - These MUST be DIFFERENT from the inline prompts — they should expand the topic into adjacent areas, offer a contrasting perspective, or go one level deeper
  - Think: "What would a curious learner naturally ask next after exploring the inline prompts?"

PROMPT QUALITY RULES (CRITICAL — follow these exactly):
- Every suggested prompt (both inline and follow-up) MUST be at least 25 words long
- Every prompt MUST start with a role instruction (e.g., "Act as a...", "Imagine you are a...")
- Every prompt MUST include the specific topic, a clear task, and at least one constraint or deliverable
- NEVER suggest short or vague prompts like "Tell me about X" or "Explain Y"
- NEVER start a prompt with "Imagine you" and end it abruptly — always complete the full instruction
- Follow-up prompts must NOT repeat or rephrase the inline prompts — they must explore new ground

Examples of inline prompts:
- Try this prompt: "Act as a senior data engineer. Explain how choosing between open-source and proprietary AI models affects data pipeline architecture, including 3 specific trade-offs with real-world examples."

Examples of follow-up prompts (exploring adjacent territory):
- Explore further: "Act as a CTO at a mid-size startup. Compare the total cost of ownership between hosting an open-source LLM versus using a proprietary API, including compute, maintenance, and scaling considerations over 2 years."
- Explore further: "Imagine you are a machine learning engineer. Describe how to fine-tune an open-source model for a domain-specific task, covering dataset preparation, training infrastructure, and evaluation metrics."
"""

    # Regex for quoted strings that look like LLM prompts (role instructions)
    _QUOTE_RE = re.compile(r'[""\u201c\u2018]([^""\u201d\u2019]{30,})[""\u201d\u2019]')
    _ROLE_RE = re.compile(
        r'\b(?:act as|imagine you|as a|you are|suppose you|pretend you|'
        r'take the role|playing the role|from the perspective)\b',
        re.IGNORECASE,
    )

    @staticmethod
    def _clean_line(line: str) -> str:
        """Strip markdown list markers, numbering, bold from a line."""
        cleaned = line.strip()
        cleaned = re.sub(r'^[\s\-*•]+', '', cleaned)
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
        cleaned = cleaned.replace('**', '')
        return cleaned

    @staticmethod
    def _strip_quotes(text: str) -> str:
        """Strip surrounding straight and smart quotes."""
        return re.sub(r'^["\'\u201c\u2018]+|["\'\u201d\u2019]+$', '', text).strip()

    def _extract_suggested_prompts(self, response_text: str, lesson_ctx: dict) -> list[str]:
        """Extract suggested prompts from LLM response using 4-tier approach.

        Tier 1: "Explore further:" prefixed lines
        Tier 2: "Try this prompt:" / "Ask:" prefixed lines
        Tier 3: Any quoted string 30+ chars with a role instruction
        Tier 4: Context-based fallback (guaranteed non-empty)
        """
        prompts: list[str] = []

        # Tier 1: "Explore further:" prefix
        for line in response_text.split("\n"):
            cleaned = self._clean_line(line)
            m = re.match(r'explore\s+further\s*:\s*(.*)', cleaned, re.IGNORECASE)
            if m:
                text = self._strip_quotes(m.group(1).strip())
                if text and len(text) >= 20:
                    prompts.append(text)

        # Tier 2: "Try this prompt:" / "Ask:" prefix (only if Tier 1 found nothing)
        if not prompts:
            for line in response_text.split("\n"):
                cleaned = self._clean_line(line)
                m = re.match(
                    r'(?:try(?:\s+this)?\s+prompt|ask|suggested?\s+prompt)\s*:\s*(.*)',
                    cleaned, re.IGNORECASE,
                )
                if m:
                    text = self._strip_quotes(m.group(1).strip())
                    if text and len(text) >= 20:
                        prompts.append(text)

        # Tier 3: Any quoted string with a role instruction (broadest pattern)
        if not prompts:
            for match in self._QUOTE_RE.finditer(response_text):
                candidate = match.group(1).strip()
                if self._ROLE_RE.search(candidate) and len(candidate) >= 30:
                    prompts.append(candidate)
                    if len(prompts) >= 2:
                        break

        # Tier 4: Guaranteed context-based fallback
        if not prompts:
            skill = lesson_ctx.get("skill_name", "this skill")
            title = lesson_ctx.get("lesson_title", "this topic")
            prompts = [
                f'Act as a senior {skill} practitioner. Based on the concept of "{title}", '
                f'explain the 3 most common mistakes beginners make and how to avoid them, '
                f'with concrete examples from real-world projects.',
                f'Act as a learning coach specializing in {skill}. Create a 5-minute exercise '
                f'that tests whether I truly understand "{title}" or just memorized the surface-level '
                f'explanation, including a rubric for self-assessment.',
            ]

        return prompts[:2]

    async def execute(self, task: dict) -> dict:
        """Handle a mentor conversation turn.

        Args:
            task: {
                "message": str,
                "conversation_history": [{"role": "user"|"mentor", "content": str}],
                "lesson_context": {
                    "concept_snapshot": str,
                    "skill_name": str,
                    "skill_level": str,
                    "lesson_title": str
                },
                "confusion_context": str | None  # if triggered by "Confused?" button
            }

        Returns:
            {
                "response": str,
                "suggested_prompts": [str]
            }
        """
        self._start_execution()

        message = task.get("message", "")
        history = task.get("conversation_history", [])
        lesson_ctx = task.get("lesson_context", {})
        confusion = task.get("confusion_context")

        # Build context for the LLM
        context_parts = []
        if lesson_ctx:
            context_parts.append(f"CURRENT LESSON: {lesson_ctx.get('lesson_title', '')}")
            context_parts.append(f"SKILL: {lesson_ctx.get('skill_name', '')} (Level: {lesson_ctx.get('skill_level', '')})")
            if lesson_ctx.get("concept_snapshot"):
                context_parts.append(f"CONCEPT: {lesson_ctx['concept_snapshot']}")

        context_str = "\n".join(context_parts) if context_parts else "No specific lesson context."

        # Build conversation history for the LLM
        conv_context = []
        for msg in history[-10:]:  # Last 10 messages for context window
            role = "user" if msg.get("role") == "user" else "assistant"
            conv_context.append({"role": role, "content": msg.get("content", "")})

        # Build the prompt
        if confusion:
            prompt = f"""The learner clicked the "Confused" button on this section: {confusion}

Lesson context:
{context_str}

Provide:
1. A simpler explanation using an analogy
2. 2-3 suggested prompts they can try to understand better
3. One concrete example

Keep it encouraging and concise."""
        else:
            prompt = f"""Lesson context:
{context_str}

Learner's message: {message}

Respond as the AI mentor. Guide them, don't give direct answers."""

        response_text = await self._call_llm(
            prompt,
            context=conv_context if conv_context else None,
            temperature=0.7,
        )

        # ── Extract suggested prompts (4-tier approach — guarantees non-empty) ──
        suggested_prompts = self._extract_suggested_prompts(response_text, lesson_ctx)

        self._log_execution("mentor_chat", task, {"response_length": len(response_text)})
        duration = self._end_execution()

        return {
            "response": response_text,
            "suggested_prompts": suggested_prompts,
            "duration_ms": duration,
        }
