"""JD Parser Agent - Extracts State B from job descriptions.

Identifies the top 10 skills required by the target job, each mapped
to the GenAI Skills Ontology with a rationale explaining *why* the
skill is needed based on the job description text.
"""
import json
from app.agents.base import BaseAgent
from app.services.ontology import get_ontology_service


class JDParserAgent(BaseAgent):
    """Agent for parsing job descriptions and extracting required skills (State B)."""

    name = "JDParserAgent"
    description = "Parses job descriptions to extract required skills and proficiency levels"

    system_prompt = """You are an expert job description analyst specializing in AI/ML roles.
Your task is to analyze job descriptions and extract the TOP 10 required skills mapped to
the GenAI Skills Ontology.

PROFICIENCY SCALE (use this when assigning required levels):
- Level 1 (Aware): Can explain the concept. Entry-level familiarity.
- Level 2 (User): Can apply with guidance. Uses existing tools/frameworks.
- Level 3 (Practitioner): Adapts independently. Configures, customizes, troubleshoots.
- Level 4 (Builder): Ships production solutions. Designs and implements systems end-to-end.
- Level 5 (Architect): Designs systems of systems. Sets technical direction and standards.

CALIBRATION GUIDANCE:
- JD says "strong understanding of", "deep knowledge of" → Level 3 (Practitioner)
- JD says "hands-on experience building", "implement", "develop" → Level 4 (Builder)
- JD says "design systems", "lead architecture", "define strategy" → Level 5 (Architect)
- JD says "familiarity with", "awareness of", "exposure to" → Level 2 (User)
- Senior/lead/staff roles typically require Level 3-5 for core skills
- Mid-level roles typically require Level 2-4 for core skills
- Entry-level roles typically require Level 1-3 for core skills

For each identified skill requirement, determine:
1. The skill ID from the ontology
2. The required proficiency level (1-5) using the calibration guidance above
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

        # Fallback: when RAG is unavailable (NoOpRetriever), inject full ontology
        # so the LLM sees all valid skill IDs instead of hallucinating.
        ontology_context = ""
        if not relevant_skills:
            ontology = get_ontology_service()
            ontology_context = ontology.format_skills_for_prompt()

        # Build prompt
        prompt = self._build_parsing_prompt(
            jd_text, target_role, relevant_skills, ontology_context=ontology_context
        )

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

        # Post-process: validate and remap skill IDs to ontology.
        # Critical for custom profiles where the LLM may hallucinate
        # IDs despite instructions — ensures state_b is grounded.
        ontology = get_ontology_service()
        valid_ids = ontology.get_all_skill_ids()

        # Build a name lookup from the top_10 for remapping
        name_to_orig = {}
        for entry in result.get("top_10_target_skills", []):
            name_to_orig[entry.get("skill_id", "")] = entry.get("skill_name", "")

        cleaned_b = {}
        for sid, lvl in result.get("state_b_skills", {}).items():
            if sid in valid_ids:
                cleaned_b[sid] = lvl
            else:
                name = name_to_orig.get(sid, "")
                matches = ontology.search_skills(name) if name else []
                if matches:
                    cleaned_b[matches[0]["id"]] = lvl
        result["state_b_skills"] = cleaned_b

        if "top_10_target_skills" in result:
            for entry in result["top_10_target_skills"]:
                sid = entry.get("skill_id", "")
                if sid not in valid_ids:
                    name = entry.get("skill_name", "")
                    matches = ontology.search_skills(name) if name else []
                    if matches:
                        entry["skill_id"] = matches[0]["id"]
                        entry["domain"] = matches[0]["domain"]

        if "extracted_requirements" in result:
            for req in result["extracted_requirements"]:
                sid = req.get("skill_id", "")
                if sid not in valid_ids:
                    name = req.get("skill_name", "")
                    matches = ontology.search_skills(name) if name else []
                    if matches:
                        req["skill_id"] = matches[0]["id"]

        self._log_execution("parse_jd", {"jd_length": len(jd_text)}, result)
        result["duration_ms"] = self._end_execution()

        return result

    def _build_parsing_prompt(
        self, jd_text: str, target_role: str, relevant_skills: list,
        *, ontology_context: str = ""
    ) -> str:
        """Build the JD parsing prompt for the LLM."""
        if relevant_skills:
            skills_context = "\n".join([
                f"- {s['skill_id']}: {s['skill_name']} (Domain: {s['domain_label']}, Level: {s['level']})"
                for s in relevant_skills
            ])
        elif ontology_context:
            skills_context = ontology_context
        else:
            skills_context = "(No skills available)"

        return f"""Analyze this job description and identify the TOP 10 required skills.

TARGET ROLE: {target_role or 'Not specified'}

JOB DESCRIPTION:
{jd_text}

AVAILABLE SKILLS FROM ONTOLOGY:
{skills_context}

PROFICIENCY SCALE (use this to assign required_level):
- Level 1 (Aware): Can explain the concept. Entry-level familiarity.
- Level 2 (User): Can apply with guidance. Uses existing tools.
- Level 3 (Practitioner): Adapts independently. Configures, customizes, troubleshoots.
- Level 4 (Builder): Ships production solutions. Designs and implements end-to-end.
- Level 5 (Architect): Designs systems of systems. Sets technical direction.

CALIBRATION RULES:
- "strong understanding", "deep knowledge" → Level 3+
- "hands-on experience building", "implement", "develop" → Level 4
- "design systems", "lead architecture", "define strategy" → Level 5
- "familiarity with", "awareness of" → Level 2
- Senior/Lead roles: core skills should be Level 3-5
- Mid-level roles: core skills should be Level 2-4
- For HIGH importance skills, assign Level 3 minimum (the role NEEDS proficiency)
- For skills central to the role's primary function, prefer Level 4 (Builder)

INSTRUCTIONS:
CRITICAL: You MUST ONLY use skill_id values from the AVAILABLE SKILLS list above.
Do NOT invent new skill IDs. Every skill_id in your response must exactly match one from that list.
If a JD requirement doesn't map perfectly to an ontology skill, choose the closest match.

1. Select exactly 10 skills from the ontology that are most critical for this role.
2. For each skill, determine the required proficiency level (1-5) using the CALIBRATION RULES above.
   Do NOT default to low levels — match the level to the JD's actual demands.
3. For each skill, rate its importance (high/medium/low).
4. For each skill, write a rationale (1-2 sentences) explaining WHY this skill is needed,
   referencing specific text or requirements from the job description.
5. Rank the 10 skills from most important (rank 1) to least important (rank 10).
6. Also populate state_b_skills with the same skill_id → required_level mapping.
7. Also populate extracted_requirements with the same data for backward compatibility.

Example rationale: "The JD requires 'Define evaluation criteria, launch experiments, and
iterate based on performance' — this directly maps to Eval Types (offline/online/red team)
at Practitioner level (L3), as the role needs independent evaluation capability."

Include both explicit requirements and implied skills from the responsibilities.
Focus on AI/GenAI related skills but also include relevant prerequisites and soft skills.
Prioritize skills from agentic (D.AGT), evaluation (D.EVL), RAG (D.RAG), operations (D.OPS),
and security (D.SEC) domains when the JD mentions those capabilities."""
