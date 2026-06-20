"""LLM provider factory."""
from functools import lru_cache
from app.services.llm.base import BaseLLMProvider
from app.services.llm.claude import ClaudeProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.config import get_settings


@lru_cache
def get_llm_provider() -> BaseLLMProvider:
    """Get the configured LLM provider instance."""
    settings = get_settings()

    if settings.llm_provider == "claude":
        return ClaudeProvider()
    elif settings.llm_provider == "openai":
        return OpenAIProvider()
    elif settings.llm_provider == "vertex":
        from app.services.llm.vertex_provider import VertexAIProvider
        return VertexAIProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


@lru_cache
def get_judge_provider() -> BaseLLMProvider:
    """Trust Before Intelligence: the judge/evaluator runs on a PINNED, CALIBRATED
    model, independent of the generation provider. Configured via settings.judge_provider
    / settings.judge_model (default openai / gpt-4.1). Do not route judges through
    get_llm_provider() - that would couple judging to whatever generates content."""
    settings = get_settings()
    provider, model = settings.judge_provider, settings.judge_model
    if provider == "claude":
        return ClaudeProvider(model=model)
    elif provider == "openai":
        return OpenAIProvider(model=model)
    elif provider == "vertex":
        from app.services.llm.vertex_provider import VertexAIProvider
        return VertexAIProvider(model=model)
    else:
        raise ValueError(f"Unknown judge provider: {provider}")
