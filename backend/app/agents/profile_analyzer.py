"""Profile Analyzer Agent - Extracts State A from user profile."""
import json
from app.agents.base import BaseAgent


class ProfileAnalyzerAgent(BaseAgent):
    """Agent for analyzing user profiles and extracting current skill state (State A)."""

    name = "ProfileAnalyzerAgent"
    description = "Analyzes user profiles to extract current role, skills, and AI exposure level"

    system_prompt = """You are an expert career analyst specializing in AI skills assessment.
Your task is to analyze a user's professional profile and determine their current skill levels
based on the GenAI Skills Ontology.

For each skill, assign a proficiency level (0-5):
- 0: Unaware - Has not heard of it
- 1: Aware - Can explain basics
- 2: User - Can apply with help
- 3: Practitioner - Can adapt independently
- 4: Builder - Ships solutions
- 5: Architect - Designs systems

Be conservative in your assessments - only assign higher levels if there's clear evidence.
Focus on AI/GenAI related skills and their prerequisites."""

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

        # Prepare prompt for LLM
        prompt = self._build_analysis_prompt(profile, relevant_skills)

        output_schema = {
            "type": "object",
            "properties": {
                "state_a_skills": {
                    "type": "object",
                    "description": "Mapping of skill IDs to proficiency levels (0-5)"
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
            "required": ["state_a_skills", "profile_summary", "recommended_focus_domains"]
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

        return " | ".join(parts)

    def _build_analysis_prompt(self, profile: dict, relevant_skills: list) -> str:
        """Build the analysis prompt for the LLM."""
        skills_context = "\n".join([
            f"- {s['skill_id']}: {s['skill_name']} (Domain: {s['domain_label']}, Base Level: {s['level']})"
            for s in relevant_skills[:30]
        ])

        return f"""Analyze this professional profile and assess their current skill levels.

PROFILE:
Name: {profile.get('name', 'Unknown')}
Current Role: {profile.get('current_role', 'Unknown')}
Industry: {profile.get('industry', 'Unknown')}
Experience: {profile.get('experience_years', 'Unknown')} years
AI Exposure: {profile.get('ai_exposure_level', 'Unknown')}

Background:
{json.dumps(profile.get('current_profile', {}), indent=2)}

Learning Intent:
{profile.get('learning_intent', 'Not specified')}

RELEVANT SKILLS TO ASSESS:
{skills_context}

Based on this profile, assess the user's current proficiency level (0-5) for each relevant skill.
Only include skills where you have enough information to make an assessment.
Be conservative - don't assign high levels without clear evidence."""
