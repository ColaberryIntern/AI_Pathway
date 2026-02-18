"""JD Parser Agent - Extracts State B from job descriptions."""
import json
from app.agents.base import BaseAgent


class JDParserAgent(BaseAgent):
    """Agent for parsing job descriptions and extracting required skills (State B)."""

    name = "JDParserAgent"
    description = "Parses job descriptions to extract required skills and proficiency levels"

    system_prompt = """You are an expert job description analyst specializing in AI/ML roles.
Your task is to analyze job descriptions and extract the required skills mapped to the GenAI Skills Ontology.

For each identified skill requirement, determine:
1. The skill ID from the ontology
2. The required proficiency level (0-5)
3. The importance/criticality (high/medium/low)

Focus on:
- Explicit skill requirements
- Implied skills from responsibilities
- Tools and technologies mentioned
- Soft skills and collaboration requirements

Map everything to the GenAI Skills Ontology structure."""

    async def execute(self, task: dict) -> dict:
        """Parse a job description and extract State B skills.

        Args:
            task: {
                "jd_text": str - Job description text
                "target_role": str - Target role title (optional)
            }

        Returns:
            {
                "state_b_skills": dict - Skill IDs mapped to required levels
                "extracted_requirements": list - Detailed skill requirements
                "role_analysis": dict - Analysis of the role
            }
        """
        self._start_execution()

        jd_text = task.get("jd_text", "")
        target_role = task.get("target_role", "")

        # Get similar JDs and relevant skills from RAG
        relevant_skills = await self.rag.retrieve_skills(jd_text, n_results=40)

        # Build prompt
        prompt = self._build_parsing_prompt(jd_text, target_role, relevant_skills)

        output_schema = {
            "type": "object",
            "properties": {
                "state_b_skills": {
                    "type": "object",
                    "description": "Mapping of skill IDs to required proficiency levels (0-5)"
                },
                "extracted_requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill_id": {"type": "string"},
                            "skill_name": {"type": "string"},
                            "required_level": {"type": "integer"},
                            "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                            "evidence": {"type": "string"}
                        }
                    },
                    "description": "Detailed breakdown of skill requirements"
                },
                "role_analysis": {
                    "type": "object",
                    "properties": {
                        "primary_function": {"type": "string"},
                        "key_domains": {"type": "array", "items": {"type": "string"}},
                        "seniority_level": {"type": "string"},
                        "technical_depth": {"type": "string"}
                    }
                },
                "industry": {"type": "string"},
                "experience_level": {"type": "string"}
            },
            "required": ["state_b_skills", "extracted_requirements", "role_analysis"]
        }

        result = await self._call_llm_structured(prompt, output_schema)

        self._log_execution("parse_jd", {"jd_length": len(jd_text)}, result)
        result["duration_ms"] = self._end_execution()

        return result

    def _build_parsing_prompt(
        self, jd_text: str, target_role: str, relevant_skills: list
    ) -> str:
        """Build the JD parsing prompt for the LLM."""
        skills_context = "\n".join([
            f"- {s['skill_id']}: {s['skill_name']} (Domain: {s['domain_label']})"
            for s in relevant_skills
        ])

        return f"""Analyze this job description and extract the required skills.

TARGET ROLE: {target_role or 'Not specified'}

JOB DESCRIPTION:
{jd_text}

AVAILABLE SKILLS FROM ONTOLOGY:
{skills_context}

For each requirement in the JD:
1. Map it to the most appropriate skill ID from the ontology
2. Determine the required proficiency level (1-5)
3. Rate its importance (high/medium/low)
4. Note the evidence from the JD

Include both explicit requirements and implied skills from the responsibilities.
Focus on AI/GenAI related skills but also include relevant prerequisites and soft skills."""
