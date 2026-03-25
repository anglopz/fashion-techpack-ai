"""OpenRouter LLM client with model routing by task type."""

from __future__ import annotations

from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import Settings, get_settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Thin wrapper around the OpenAI SDK pointed at OpenRouter."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = AsyncOpenAI(
            api_key=self._settings.openrouter_api_key,
            base_url=self._settings.openrouter_base_url,
        )

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        task_type: str,
        **kwargs: Any,
    ) -> str:
        """Send a chat completion request routed to the model for *task_type*.

        Returns the assistant message content as a string.
        """
        model = self._settings.models.get_model(task_type)
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def structured_output(
        self,
        messages: list[dict[str, str]],
        task_type: str,
        response_model: type[T],
        **kwargs: Any,
    ) -> T:
        """Request a chat completion and parse the response into *response_model*.

        Uses ``response_format`` with a JSON schema so the model returns
        structured JSON that is validated by the Pydantic model.
        """
        model = self._settings.models.get_model(task_type)
        response = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": response_model.model_json_schema(),
                },
            },
            **kwargs,
        )
        raw = response.choices[0].message.content or "{}"
        return response_model.model_validate_json(raw)
