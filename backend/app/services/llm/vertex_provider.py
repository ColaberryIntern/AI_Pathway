"""Vertex AI (Gemini) LLM provider implementation."""
import json
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from app.services.llm.base import BaseLLMProvider, LLMResponse
from app.config import get_settings


class VertexAIProvider(BaseLLMProvider):
    """Vertex AI (Gemini) LLM provider."""

    def __init__(self):
        settings = get_settings()
        # Initialize Vertex AI
        vertexai.init(
            project=settings.gcp_project_id,
            location=settings.gcp_region,
        )
        self.model_name = settings.vertex_model
        self.model = GenerativeModel(self.model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        context: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate response using Vertex AI Gemini."""
        # Cap max_tokens to Gemini's limit (8192)
        max_tokens = min(max_tokens, 8192)

        # Build the conversation history
        contents = []

        # Add context messages if provided
        if context:
            for msg in context:
                role = msg.get("role", "user")
                # Gemini uses "user" and "model" roles
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": msg.get("content", "")}],
                })

        # Build the final prompt with system instructions
        final_prompt = prompt
        if system_prompt:
            final_prompt = f"{system_prompt}\n\n{prompt}"
        if json_mode:
            final_prompt += "\n\nRespond with valid JSON only. No other text."

        contents.append({
            "role": "user",
            "parts": [{"text": final_prompt}],
        })

        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain",
        )

        # Generate response
        response = await self.model.generate_content_async(
            contents=contents,
            generation_config=generation_config,
        )

        content = response.text if response.text else ""

        # Extract usage information if available
        usage = None
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = {
                "input_tokens": response.usage_metadata.prompt_token_count,
                "output_tokens": response.usage_metadata.candidates_token_count,
            }

        return LLMResponse(
            content=content,
            raw_response=response,
            usage=usage,
            model=self.model_name,
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
        """Generate structured JSON output using Vertex AI Gemini."""
        schema_str = json.dumps(output_schema, indent=2)

        structured_system = f"""You are a helpful assistant that outputs structured JSON data.

{system_prompt or ''}

You must respond with valid JSON that matches this schema:
{schema_str}

Respond with ONLY the JSON object, no additional text or markdown formatting.
IMPORTANT: Ensure your response is complete and valid JSON."""

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
