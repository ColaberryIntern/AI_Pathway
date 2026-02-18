"""OpenAI LLM provider implementation."""
import json
from openai import AsyncOpenAI
from app.services.llm.base import BaseLLMProvider, LLMResponse
from app.config import get_settings


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate response using OpenAI."""
        # Cap max_tokens to OpenAI's output limit (16384 for gpt-4o)
        max_tokens = min(max_tokens, 16384)
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add context messages if provided
        if context:
            for msg in context:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Add main prompt
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content if response.choices else ""

        return LLMResponse(
            content=content,
            raw_response=response,
            usage={
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            },
            model=self.model,
        )

    async def generate_structured(
        self,
        prompt: str,
        output_schema: dict,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        temperature: float = 0.3,
        max_tokens: int = 8192,
    ) -> dict:
        """Generate structured JSON output using OpenAI."""
        schema_str = json.dumps(output_schema, indent=2)

        structured_system = f"""You are a helpful assistant that outputs structured JSON data.

{system_prompt or ''}

You must respond with valid JSON that matches this schema:
{schema_str}

Respond with ONLY the JSON object."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=structured_system,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )

        return json.loads(response.content.strip())
