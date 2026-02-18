"""Assessment Agent - Generates and scores skill assessments."""
import json
from app.agents.base import BaseAgent


class AssessmentAgent(BaseAgent):
    """Agent for generating and scoring skill assessment quizzes."""

    name = "AssessmentAgent"
    description = "Generates adaptive quiz questions and scores responses to refine skill levels"

    system_prompt = """You are an expert AI skills assessor. Your task is to generate
assessment questions that accurately measure a person's proficiency level in specific skills.

For each skill, create questions that can distinguish between proficiency levels:
- Level 1 (Aware): Basic concept recognition
- Level 2 (User): Can apply with guidance
- Level 3 (Practitioner): Can adapt independently
- Level 4 (Builder): Ships solutions
- Level 5 (Architect): Designs systems

Generate a mix of:
1. Multiple choice questions for concept understanding
2. Scenario-based questions for practical application
3. Self-assessment questions for experience validation"""

    async def execute(self, task: dict) -> dict:
        """Generate assessment questions or score responses.

        Args:
            task: {
                "action": "generate" | "score"
                "skill_ids": list - Skills to assess (for generate)
                "responses": list - Quiz responses (for score)
                "questions": list - Original questions (for score)
            }

        Returns:
            For generate: {"questions": list}
            For score: {"skill_scores": dict, "state_a_skills": dict}
        """
        self._start_execution()

        action = task.get("action", "generate")

        if action == "generate":
            result = await self._generate_questions(task)
        else:
            result = await self._score_responses(task)

        self._log_execution(f"assessment_{action}", task, result)
        result["duration_ms"] = self._end_execution()

        return result

    async def _generate_questions(self, task: dict) -> dict:
        """Generate assessment questions for given skills."""
        skill_ids = task.get("skill_ids", [])
        industry = task.get("industry", "")
        num_questions = task.get("num_questions", 3)

        # Get skill details from RAG
        skill_context = []
        for skill_id in skill_ids[:10]:  # Limit to 10 skills
            skills = await self.rag.retrieve_skills(skill_id, n_results=1)
            if skills:
                skill_context.append(skills[0])

        prompt = f"""Generate assessment questions for these skills.
Industry context: {industry or 'General'}

SKILLS TO ASSESS:
{json.dumps(skill_context, indent=2)}

For each skill, generate {num_questions} questions:
1. One concept question (multiple choice)
2. One scenario question (multiple choice)
3. One self-assessment question

Each question should help determine the person's proficiency level (1-5)."""

        output_schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "skill_id": {"type": "string"},
                            "skill_name": {"type": "string"},
                            "question": {"type": "string"},
                            "question_type": {
                                "type": "string",
                                "enum": ["multiple_choice", "scenario", "self_assessment"]
                            },
                            "options": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "text": {"type": "string"},
                                        "level_indicator": {"type": "integer"}
                                    }
                                }
                            },
                            "correct_answer": {"type": "string"}
                        }
                    }
                }
            }
        }

        return await self._call_llm_structured(prompt, output_schema)

    async def _score_responses(self, task: dict) -> dict:
        """Score quiz responses and determine skill levels."""
        questions = task.get("questions", [])
        responses = task.get("responses", [])

        prompt = f"""Score these assessment responses and determine skill proficiency levels.

QUESTIONS AND RESPONSES:
{json.dumps([{"question": q, "response": r} for q, r in zip(questions, responses)], indent=2)}

For each skill assessed:
1. Analyze the responses
2. Determine the demonstrated proficiency level (0-5)
3. Provide confidence in the assessment

Return the assessed skill levels."""

        output_schema = {
            "type": "object",
            "properties": {
                "skill_scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill_id": {"type": "string"},
                            "assessed_level": {"type": "integer"},
                            "confidence": {"type": "number"},
                            "reasoning": {"type": "string"}
                        }
                    }
                },
                "state_a_skills": {
                    "type": "object",
                    "description": "Final skill ID to level mapping"
                }
            }
        }

        return await self._call_llm_structured(prompt, output_schema)
