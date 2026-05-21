"""Claude AI service for agent interactions."""
import json
import asyncio
from typing import TypeVar, Type, Optional, AsyncGenerator
from pydantic import BaseModel
from anthropic import Anthropic
from app.core.config import Settings

T = TypeVar("T", bound=BaseModel)


class ClaudeService:
    """Service wrapping Anthropic Claude API for structured generation."""

    def __init__(self, settings: Settings):
        self.client = Anthropic(api_key=settings.CLAUDE_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS

    def _build_structured_prompt(self, system_prompt: str, user_prompt: str, output_model: Type[T]) -> str:
        schema_json = output_model.model_json_schema()
        return (
            f"{system_prompt}\n\n"
            f"Respond with a valid JSON object conforming to this schema:\n"
            f"{json.dumps(schema_json, indent=2)}\n\n"
            f"User request:\n{user_prompt}\n\n"
            f"JSON response:"
        )

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: Type[T],
        max_retries: int = 2
    ) -> T:
        """Generate a structured response from Claude."""
        prompt = self._build_structured_prompt(system_prompt, user_prompt, output_model)

        for attempt in range(max_retries + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                content = response.content[0].text

                # Extract JSON from response
                json_str = content.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()

                data = json.loads(json_str)
                return output_model.model_validate(data)

            except (json.JSONDecodeError, Exception) as e:
                if attempt < max_retries:
                    continue
                raise RuntimeError(f"Failed to generate structured output after {max_retries + 1} attempts: {e}")

    async def generate_structured_async(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: Type[T],
        max_retries: int = 2
    ) -> T:
        """Async version of generate_structured."""
        return await asyncio.to_thread(
            self.generate_structured, system_prompt, user_prompt, output_model, max_retries
        )

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Generate free-form text from Claude."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    async def generate_text_async(self, system_prompt: str, user_prompt: str) -> str:
        """Async version of generate_text."""
        return await asyncio.to_thread(self.generate_text, system_prompt, user_prompt)
