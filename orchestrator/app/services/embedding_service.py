"""Embedding service using OpenRouter with text-embedding-3-small."""

from __future__ import annotations

from openai import AsyncOpenAI

from app.config import Settings, get_settings


class EmbeddingService:
    """Generate text embeddings via OpenRouter (OpenAI-compatible API)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = AsyncOpenAI(
            api_key=self._settings.openrouter_api_key,
            base_url=self._settings.openrouter_base_url,
        )
        self._model = self._settings.models.embedding

    async def embed_text(self, text: str) -> list[float]:
        """Return a 1536-dimensional embedding vector for *text*."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for a batch of texts."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]
