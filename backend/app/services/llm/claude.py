"""Claude LLM provider implementation."""
import json
from anthropic import AsyncAnthropic
from app.services.llm.base import BaseLLMProvider, LLMResponse
from app.config import get_settings


class ClaudeProvider(BaseLLMProvider):
    """Claude/Anthropic LLM provider."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate response using Claude."""
        messages = []

        # Add context messages if provided
        if context:
            for msg in context:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Add main prompt
        messages.append({"role": "user", "content": prompt})

        # Prepare system prompt
        final_system = system_prompt or ""
        if json_mode:
            final_system += "\n\nYou must respond with valid JSON only. No other text."

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=final_system if final_system else None,
            messages=messages,
        )

        content = response.content[0].text if response.content else ""

        return LLMResponse(
            content=content,
            raw_response=response,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
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
        """Generate structured JSON output using Claude."""
        schema_str = json.dumps(output_schema, indent=2)

        structured_system = f"""You are a helpful assistant that outputs structured JSON data.

{system_prompt or ''}

IMPORTANT: Respond with a JSON object containing ACTUAL DATA VALUES (real strings, arrays, objects with real content). Do NOT echo back the schema definition — fill in real values for each field.

The JSON structure must match this schema:
{schema_str}

Respond with ONLY the populated JSON object with real content values. No additional text or markdown formatting."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=structured_system,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )

        # Parse JSON response
        content = response.content.strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to repair truncated JSON
            import re
            # Try to close any unclosed structures
            open_braces = content.count('{') - content.count('}')
            open_brackets = content.count('[') - content.count(']')

            # Simple repair: close open structures
            repaired = content.rstrip(',')  # Remove trailing comma
            repaired += ']' * open_brackets
            repaired += '}' * open_braces

            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                # Return error dict if repair fails
                raise ValueError(f"Failed to parse LLM response as JSON: {str(e)[:100]}")
