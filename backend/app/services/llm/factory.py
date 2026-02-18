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
