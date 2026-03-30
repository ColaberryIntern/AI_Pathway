"""JD profile parser service — extracts structured target profile from job descriptions.

Uses the configured LLM provider to analyze JD text and extract
technical skills, soft skills, AI requirements, and a role summary.
"""
import json
import logging

logger = logging.getLogger(__name__)


async def parse_jd_profile(jd_text: str, target_role: str = "") -> dict:
    """Parse a job description and extract a structured target profile.

    Returns:
        {
            "target_role": str,
            "technical_skills": list[str],
            "soft_skills": list[str],
            "ai_requirements": str | None,
            "summary": str | None,
            "seniority_level": str | None,
            "key_tools": list[str],
        }
    """
    if not jd_text.strip():
        raise ValueError("No job description text provided.")

    # Truncate to avoid token limits
    jd_text = jd_text[:8000]

    from app.services.llm import get_llm_provider

    llm = get_llm_provider()

    system_prompt = (
        "You are a job description analyst. Extract structured profile information "
        "from the job description text provided. Return ONLY a JSON object with "
        "the specified fields. If a field cannot be determined, use null or an empty array."
    )

    prompt = f"""Analyze this job description and extract the following fields:

1. "target_role" — The exact job title for this position. Extract from the title field, first sentence, or "We are looking for a [TITLE]" pattern. If no explicit title, infer the best role title from the responsibilities. (e.g. "Lead AI Solution Architect", "AI Content Editor", "Senior Data Scientist")
2. "technical_skills" — Array of 4-10 key technical skills, tools, and technologies required (e.g. ["Python", "TensorFlow", "AWS", "SQL", "Docker"]). Extract the most prominent ones.
3. "soft_skills" — Array of 3-6 soft/leadership skills required or implied (e.g. ["Cross-functional collaboration", "Strategic thinking", "Stakeholder management"]).
4. "ai_requirements" — One or two sentences describing the AI/ML experience or capabilities expected for this role. If the role doesn't involve AI, describe the key technical competency expected.
5. "summary" — A 2-3 sentence summary of what this role entails and what the ideal candidate looks like. Write in third person.
6. "seniority_level" — One of: "Entry-level", "Mid-level", "Senior", "Lead", "Director", "VP/Executive", or null.
7. "key_tools" — Array of 2-5 specific platforms, frameworks, or tools mentioned (e.g. ["OpenAI API", "LangChain", "Kubernetes", "Snowflake"]). Different from technical_skills — these are specific named products/platforms.

{f'TARGET ROLE: {target_role}' if target_role else ''}

JOB DESCRIPTION:
{jd_text}

Return ONLY a JSON object with these 7 keys. No additional text."""

    response = await llm.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.1,
        max_tokens=2048,
        json_mode=True,
    )

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        logger.error("LLM returned non-JSON response: %s", response.content[:200])
        raise ValueError("Failed to parse job description. Please try again.")

    return {
        "target_role": result.get("target_role") or "",
        "technical_skills": _validate_list(result.get("technical_skills")),
        "soft_skills": _validate_list(result.get("soft_skills")),
        "ai_requirements": result.get("ai_requirements") or None,
        "summary": result.get("summary") or None,
        "seniority_level": _validate_seniority(result.get("seniority_level")),
        "key_tools": _validate_list(result.get("key_tools")),
    }


def _validate_list(value) -> list[str]:
    """Validate and normalize a list of strings."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if item and str(item).strip()]


def _validate_seniority(value) -> str | None:
    """Validate seniority level."""
    valid = {"Entry-level", "Mid-level", "Senior", "Lead", "Director", "VP/Executive"}
    if value in valid:
        return value
    return None
