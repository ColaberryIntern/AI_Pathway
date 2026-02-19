"""Profile Analyzer Agent - Extracts State A from user profile.

Identifies the user's top 10 current AI-related skills mapped to the
GenAI Skills Ontology, each with a rationale explaining *why* the skill
was identified based on the user's resume, role, and intake answers.
"""
import json
from app.agents.base import BaseAgent
from app.services.ontology import get_ontology_service


class ProfileAnalyzerAgent(BaseAgent):
    """Agent for analyzing user profiles and extracting current skill state (State A)."""

    name = "ProfileAnalyzerAgent"
    description = "Analyzes user profiles to extract current role, skills, and AI exposure level"

    system_prompt = """You are an expert career analyst specializing in AI skills assessment.
Your task is to analyze a user's professional profile and determine their top 10 current
skills based on the GenAI Skills Ontology.

For each skill, assign a proficiency level (0-5):
- 0: Unaware - Has not heard of it
- 1: Aware - Can explain basics
- 2: User - Can apply with help
- 3: Practitioner - Can adapt independently
- 4: Builder - Ships solutions
- 5: Architect - Designs systems

Be conservative in your assessments - only assign higher levels if there's clear evidence.
Focus on AI/GenAI related skills and their prerequisites.

For EACH skill you identify, provide a rationale that references specific evidence from
the user's profile (job title, responsibilities, tools used, or background)."""

    async def execute(self, task: dict) -> dict:
        """Analyze a user profile and extract State A skills.

        Args:
            task: {
                "profile": dict - User profile data
                "ontology_skills": list - Available skills from ontology
            }

        Returns:
            {
                "state_a_skills": dict - Skill IDs mapped to proficiency levels
                "top_10_current_skills": list - Top 10 skills with rationale
                "profile_summary": str - Summary of the profile
                "recommended_focus_domains": list - Domains to focus on
            }
        """
        self._start_execution()

        profile = task.get("profile", {})
        ontology_skills = task.get("ontology_skills", [])

        # Get relevant skills from RAG
        profile_summary = self._create_profile_summary(profile)
        relevant_skills = await self.rag.retrieve_skills(profile_summary, n_results=50)

        # Fallback: when RAG is unavailable (NoOpRetriever), inject full ontology
        # so the LLM sees all valid skill IDs instead of hallucinating.
        ontology_context = ""
        if not relevant_skills:
            ontology = get_ontology_service()
            ontology_context = ontology.format_skills_for_prompt()

        # Prepare prompt for LLM
        prompt = self._build_analysis_prompt(
            profile, relevant_skills, ontology_context=ontology_context
        )

        output_schema = {
            "type": "object",
            "properties": {
                "top_10_current_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer", "description": "Priority rank 1-10"},
                            "skill_id": {"type": "string", "description": "Ontology skill ID (e.g. SK.FND.001)"},
                            "skill_name": {"type": "string"},
                            "domain": {"type": "string", "description": "Domain ID (e.g. D.FND)"},
                            "domain_label": {"type": "string", "description": "Human-readable domain name"},
                            "current_level": {"type": "integer", "description": "Assessed proficiency 0-5"},
                            "rationale": {"type": "string", "description": "Why this skill was identified, referencing the user's profile"}
                        },
                        "required": ["rank", "skill_id", "skill_name", "domain", "current_level", "rationale"]
                    },
                    "minItems": 10,
                    "maxItems": 10,
                    "description": "Exactly 10 skills ranked by relevance to the user's current role"
                },
                "state_a_skills": {
                    "type": "object",
                    "description": "Mapping of skill IDs to proficiency levels (0-5) — same skills as top_10_current_skills"
                },
                "profile_summary": {
                    "type": "string",
                    "description": "Brief summary of the user's background"
                },
                "ai_exposure_assessment": {
                    "type": "string",
                    "description": "Assessment of current AI/GenAI exposure"
                },
                "recommended_focus_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Domain IDs to focus on for learning"
                }
            },
            "required": ["top_10_current_skills", "state_a_skills", "profile_summary", "recommended_focus_domains"]
        }

        result = await self._call_llm_structured(prompt, output_schema)

        # Merge with any pre-defined skills from profile
        if "estimated_current_skills" in profile:
            result["state_a_skills"] = {
                **result.get("state_a_skills", {}),
                **profile["estimated_current_skills"]
            }

        self._log_execution("analyze_profile", profile, result)
        result["duration_ms"] = self._end_execution()

        return result

    def _create_profile_summary(self, profile: dict) -> str:
        """Create a searchable summary of the profile."""
        parts = [
            f"Role: {profile.get('current_role', 'Unknown')}",
            f"Industry: {profile.get('industry', 'Unknown')}",
            f"Experience: {profile.get('experience_years', 'Unknown')} years",
        ]

        if "current_profile" in profile:
            cp = profile["current_profile"]
            if "summary" in cp:
                parts.append(f"Background: {cp['summary']}")
            if "technical_skills" in cp:
                parts.append(f"Technical skills: {', '.join(cp['technical_skills'])}")

        current_jd = profile.get("current_jd", "")
        if current_jd:
            parts.append(f"Current job description: {current_jd}")

        return " | ".join(parts)

    def _build_analysis_prompt(
        self, profile: dict, relevant_skills: list, *, ontology_context: str = ""
    ) -> str:
        """Build the analysis prompt for the LLM."""
        if relevant_skills:
            skills_context = "\n".join([
                f"- {s['skill_id']}: {s['skill_name']} (Domain: {s['domain_label']}, Base Level: {s['level']})"
                for s in relevant_skills[:30]
            ])
        elif ontology_context:
            skills_context = ontology_context
        else:
            skills_context = "(No skills available)"

        current_jd_section = ""
        current_jd = profile.get("current_jd", "")
        if current_jd:
            current_jd_section = f"\nCurrent Job Description:\n{current_jd}\n"

        # Include the 3 intake question answers if available
        intake_section = ""
        intake_parts = []
        if profile.get("ai_exposure_level"):
            intake_parts.append(f"AI Knowledge Level: {profile['ai_exposure_level']}")
        if profile.get("tools_used"):
            tools = profile["tools_used"]
            if isinstance(tools, list):
                tools = ", ".join(tools)
            intake_parts.append(f"AI Tools Used: {tools}")
        if profile.get("technical_background"):
            intake_parts.append(f"Technical/Coding Background: {profile['technical_background']}")
        if intake_parts:
            intake_section = "\nIntake Answers:\n" + "\n".join(intake_parts) + "\n"

        return f"""Analyze this professional profile and identify their TOP 10 current AI-related skills.

PROFILE:
Name: {profile.get('name', 'Unknown')}
Current Role: {profile.get('current_role', 'Unknown')}
Industry: {profile.get('industry', 'Unknown')}
Experience: {profile.get('experience_years', 'Unknown')} years
AI Exposure: {profile.get('ai_exposure_level', 'Unknown')}

Background:
{json.dumps(profile.get('current_profile', {}), indent=2)}
{current_jd_section}{intake_section}
Learning Intent:
{profile.get('learning_intent', 'Not specified')}

AVAILABLE SKILLS FROM ONTOLOGY:
{skills_context}

PROFICIENCY SCALE:
- Level 0 (Unaware): Has not heard of it.
- Level 1 (Aware): Can explain the basic concept.
- Level 2 (User): Can apply the skill with guidance or help.
- Level 3 (Practitioner): Can adapt and apply independently. Configures, troubleshoots.
- Level 4 (Builder): Ships production solutions. Implements end-to-end.
- Level 5 (Architect): Designs systems of systems. Sets technical direction.

CALIBRATION GUIDANCE:
- "Uses ChatGPT/Copilot daily" → Prompt Engineering basics at Level 3 (Practitioner)
- "Manages AI projects" → AI Product Management at Level 3-4
- "Has built ML models" → relevant skills at Level 4 (Builder)
- "Aware of but hasn't used" → Level 1 (Aware)
- "Has tried/experimented with" → Level 2 (User)
- Years of experience matter: 5+ years in a domain = Level 3+ in related skills

INSTRUCTIONS:
CRITICAL: You MUST ONLY use skill_id values from the AVAILABLE SKILLS list above.
Do NOT invent new skill IDs. Every skill_id in your response must exactly match one from that list.
If a user capability doesn't map perfectly to an ontology skill, choose the closest match.

1. Select exactly 10 skills from the ontology that best represent this user's current capabilities.
2. For each skill, assess their current proficiency level (0-5) using the PROFICIENCY SCALE above.
3. For each skill, write a rationale (1-2 sentences) explaining WHY you identified this skill,
   referencing specific evidence from their role, experience, tools used, or background.
4. Rank the 10 skills from most relevant (rank 1) to least relevant (rank 10).
5. Also populate state_a_skills with the same skill_id → level mapping.
6. Be conservative — only assign higher levels with clear evidence from the profile.
   However, do not underestimate: experienced professionals who USE AI tools daily
   are at least Level 2-3, not Level 1.

Example rationale: "User's role as Program Manager at an AI consulting firm involves
coordinating AI training programs — this directly maps to AI Enablement & Training Strategy
at Practitioner level (L3)."
"""
