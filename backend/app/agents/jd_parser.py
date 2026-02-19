"""JD Parser Agent - Extracts State B from job descriptions.

Identifies the top 10 skills required by the target job, each mapped
to the GenAI Skills Ontology with a rationale explaining *why* the
skill is needed based on the job description text.
"""
import json
from app.agents.base import BaseAgent


class JDParserAgent(BaseAgent):
    """Agent for parsing job descriptions and extracting required skills (State B)."""

    name = "JDParserAgent"
    description = "Parses job descriptions to extract required skills and proficiency levels"

    system_prompt = """You are an expert job description analyst specializing in AI/ML roles.
Your task is to analyze job descriptions and extract the TOP 10 required skills mapped to
the GenAI Skills Ontology.

For each identified skill requirement, determine:
1. The skill ID from the ontology
2. The required proficiency level (0-5)
3. The importance/criticality (high/medium/low)
4. A rationale explaining WHY this skill is needed, referencing specific text from the JD

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
                "top_10_target_skills": list - Top 10 skills with rationale
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
                "top_10_target_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer", "description": "Priority rank 1-10"},
                            "skill_id": {"type": "string", "description": "Ontology skill ID (e.g. SK.PRM.010)"},
                            "skill_name": {"type": "string"},
                            "domain": {"type": "string", "description": "Domain ID (e.g. D.PRM)"},
                            "domain_label": {"type": "string", "description": "Human-readable domain name"},
                            "required_level": {"type": "integer", "description": "Required proficiency 1-5"},
                            "importance": {"type": "string", "enum": ["high", "medium", "low"]},
                            "rationale": {"type": "string", "description": "Why this skill is needed, referencing the JD text"}
                        },
                        "required": ["rank", "skill_id", "skill_name", "domain", "required_level", "importance", "rationale"]
                    },
                    "minItems": 10,
                    "maxItems": 10,
                    "description": "Exactly 10 skills ranked by importance to the target role"
                },
                "state_b_skills": {
                    "type": "object",
                    "description": "Mapping of skill IDs to required proficiency levels (0-5) — same skills as top_10_target_skills"
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
            "required": ["top_10_target_skills", "state_b_skills", "extracted_requirements", "role_analysis"]
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
            f"- {s['skill_id']}: {s['skill_name']} (Domain: {s['domain_label']}, Level: {s['level']})"
            for s in relevant_skills
        ])

        return f"""Analyze this job description and identify the TOP 10 required skills.

TARGET ROLE: {target_role or 'Not specified'}

JOB DESCRIPTION:
{jd_text}

AVAILABLE SKILLS FROM ONTOLOGY:
{skills_context}

INSTRUCTIONS:
1. Select exactly 10 skills from the ontology that are most critical for this role.
2. For each skill, determine the required proficiency level (1-5).
3. For each skill, rate its importance (high/medium/low).
4. For each skill, write a rationale (1-2 sentences) explaining WHY this skill is needed,
   referencing specific text or requirements from the job description.
5. Rank the 10 skills from most important (rank 1) to least important (rank 10).
6. Also populate state_b_skills with the same skill_id → required_level mapping.
7. Also populate extracted_requirements with the same data for backward compatibility.

Example rationale: "The JD requires 'Define evaluation criteria, launch experiments, and
iterate based on performance' — this directly maps to Eval Types (offline/online/red team)
at Practitioner level, as the role needs hands-on evaluation capability."

Include both explicit requirements and implied skills from the responsibilities.
Focus on AI/GenAI related skills but also include relevant prerequisites and soft skills."""
