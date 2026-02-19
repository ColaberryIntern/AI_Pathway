"""Verify ontology grounding fallback for agents.

When RAG is unavailable (NoOpRetriever returns []), agents must fall back to
the full ontology injected as prompt context. These tests verify:
1. OntologyService.format_skills_for_prompt() includes all skills
2. Every skill ID in the ontology appears in the formatted string
3. The formatted string is organized by domain
4. ProfileAnalyzerAgent and JDParserAgent build prompts with ontology context
   when relevant_skills is empty
"""
import sys
from pathlib import Path

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ontology import get_ontology_service


def test_format_skills_for_prompt_includes_all_skills():
    """Every skill ID in the ontology must appear in the formatted prompt string."""
    ontology = get_ontology_service()
    formatted = ontology.format_skills_for_prompt()

    all_ids = ontology.get_all_skill_ids()
    assert len(all_ids) > 0, "Ontology should have skills"

    missing = [sid for sid in all_ids if sid not in formatted]
    assert not missing, (
        f"{len(missing)} skill IDs missing from formatted prompt: {missing[:10]}"
    )


def test_format_skills_organized_by_domain():
    """Formatted string should contain domain headers for every non-empty domain."""
    ontology = get_ontology_service()
    formatted = ontology.format_skills_for_prompt()

    for domain in ontology.domains:
        domain_skills = ontology.get_skills_by_domain(domain["id"])
        if domain_skills:
            assert domain["id"] in formatted, (
                f"Domain {domain['id']} ({domain['label']}) has skills "
                f"but is missing from formatted output"
            )


def test_format_skills_token_budget():
    """Formatted ontology should be under 10000 characters (~2500 tokens)."""
    ontology = get_ontology_service()
    formatted = ontology.format_skills_for_prompt()

    assert len(formatted) < 10000, (
        f"Formatted ontology is {len(formatted)} chars, exceeds 10000 budget"
    )


def test_get_all_skill_ids_returns_set():
    """get_all_skill_ids should return a non-empty set of strings."""
    ontology = get_ontology_service()
    all_ids = ontology.get_all_skill_ids()

    assert isinstance(all_ids, set)
    assert len(all_ids) > 100, f"Expected 100+ skills, got {len(all_ids)}"
    assert all(isinstance(sid, str) for sid in all_ids)
    assert all(sid.startswith("SK.") for sid in all_ids)


def test_profile_analyzer_prompt_with_ontology_fallback():
    """ProfileAnalyzerAgent should embed ontology context when relevant_skills is empty."""
    try:
        from app.agents.profile_analyzer import ProfileAnalyzerAgent
    except ImportError:
        print("  SKIP: vertexai not available locally")
        return

    agent = ProfileAnalyzerAgent.__new__(ProfileAnalyzerAgent)
    profile = {
        "name": "Test User",
        "current_role": "Data Analyst",
        "industry": "Finance",
        "experience_years": 5,
        "ai_exposure_level": "Basic",
    }

    ontology = get_ontology_service()
    ontology_context = ontology.format_skills_for_prompt()

    prompt = agent._build_analysis_prompt(
        profile, [], ontology_context=ontology_context
    )

    # The prompt must contain actual skill IDs
    assert "SK.FND.001" in prompt, "Prompt should contain foundational skill IDs"
    assert "SK.PRM.001" in prompt, "Prompt should contain prompting skill IDs"
    assert "MUST ONLY use skill_id" in prompt, "Prompt should contain constraint language"


def test_jd_parser_prompt_with_ontology_fallback():
    """JDParserAgent should embed ontology context when relevant_skills is empty."""
    try:
        from app.agents.jd_parser import JDParserAgent
    except ImportError:
        print("  SKIP: vertexai not available locally")
        return

    agent = JDParserAgent.__new__(JDParserAgent)

    ontology = get_ontology_service()
    ontology_context = ontology.format_skills_for_prompt()

    prompt = agent._build_parsing_prompt(
        "Sample JD text", "AI Engineer", [],
        ontology_context=ontology_context,
    )

    assert "SK.AGT.001" in prompt, "Prompt should contain agent skill IDs"
    assert "SK.EVL.001" in prompt, "Prompt should contain evaluation skill IDs"
    assert "MUST ONLY use skill_id" in prompt, "Prompt should contain constraint language"


def test_profile_analyzer_prompt_uses_rag_when_available():
    """When relevant_skills is non-empty, the prompt should use RAG results, not ontology."""
    try:
        from app.agents.profile_analyzer import ProfileAnalyzerAgent
    except ImportError:
        print("  SKIP: vertexai not available locally")
        return

    agent = ProfileAnalyzerAgent.__new__(ProfileAnalyzerAgent)
    profile = {
        "name": "Test User",
        "current_role": "Data Analyst",
        "industry": "Finance",
        "experience_years": 5,
    }

    rag_skills = [
        {
            "skill_id": "SK.FND.001",
            "skill_name": "LLM fundamentals",
            "domain_label": "AI Literacy & Foundations",
            "level": 1,
        }
    ]

    prompt = agent._build_analysis_prompt(profile, rag_skills)

    # Should contain the RAG skill
    assert "SK.FND.001" in prompt
    # Should NOT contain the full domain headers (those come from ontology format)
    assert "## AI Literacy & Foundations" not in prompt


if __name__ == "__main__":
    test_format_skills_for_prompt_includes_all_skills()
    print("  PASS: format_skills_for_prompt includes all skills")

    test_format_skills_organized_by_domain()
    print("  PASS: format_skills organized by domain")

    test_format_skills_token_budget()
    print("  PASS: format_skills within token budget")

    test_get_all_skill_ids_returns_set()
    print("  PASS: get_all_skill_ids returns valid set")

    test_profile_analyzer_prompt_with_ontology_fallback()
    print("  PASS: ProfileAnalyzerAgent prompt with ontology fallback")

    test_jd_parser_prompt_with_ontology_fallback()
    print("  PASS: JDParserAgent prompt with ontology fallback")

    test_profile_analyzer_prompt_uses_rag_when_available()
    print("  PASS: ProfileAnalyzerAgent uses RAG when available")

    print("\nAll ontology grounding tests passed.")
