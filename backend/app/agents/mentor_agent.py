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

        # Extract follow-up prompts ("Explore further:") for the bottom chips.
        # Inline prompts ("Try this prompt:") stay in the message body and are
        # rendered by the frontend's parseMessagePrompts() — no need to extract them here.
        suggested_prompts = []
        for line in response_text.split("\n"):
            line_stripped = line.strip()
            # Strip markdown list markers: "- ", "* ", "• ", "1. ", etc.
            line_clean = line_stripped.lstrip("-*•").lstrip()
            line_clean = re.sub(r'^\d+\.\s*', '', line_clean)
            if line_clean.lower().startswith("explore further:"):
                prompt_text = line_clean.split(":", 1)[-1].strip().strip('"').strip("'")
                if prompt_text and len(prompt_text) >= 50:
                    suggested_prompts.append(prompt_text)

        # Fallback: if LLM didn't use "Explore further:" prefix, grab "Try this prompt:" ones
        if not suggested_prompts:
            for line in response_text.split("\n"):
                line_stripped = line.strip()
                line_clean = line_stripped.lstrip("-*•").lstrip()
                line_clean = re.sub(r'^\d+\.\s*', '', line_clean)
                if line_clean.lower().startswith("try this prompt:") or line_clean.lower().startswith("try:"):
                    prompt_text = line_clean.split(":", 1)[-1].strip().strip('"').strip("'")
                    if prompt_text and len(prompt_text) >= 50:
                        suggested_prompts.append(prompt_text)

        self._log_execution("mentor_chat", task, {"response_length": len(response_text)})
        duration = self._end_execution()

        return {
            "response": response_text,
            "suggested_prompts": suggested_prompts,
            "duration_ms": duration,
        }
