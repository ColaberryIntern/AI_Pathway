"""Base LLM provider interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    """Response from LLM provider."""

    content: str
    raw_response: Any = None
    usage: dict | None = None
    model: str | None = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt/query
            system_prompt: System instructions for the model
            context: List of previous messages for context
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            json_mode: Whether to enforce JSON output

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        output_schema: dict,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        temperature: float = 0.3,
    ) -> dict:
        """Generate structured JSON output.

        Args:
            prompt: The user prompt/query
            output_schema: JSON schema for expected output
            system_prompt: System instructions
            context: Previous messages
            temperature: Sampling temperature

        Returns:
            Parsed JSON dictionary
        """
        pass
