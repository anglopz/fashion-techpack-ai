"""Tests for the embedding service with mocked OpenAI SDK."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import Settings
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def settings():
    return Settings(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.ai/api/v1",
    )


@pytest.fixture
def mock_openai_client():
    return AsyncMock()


@pytest.fixture
def service(settings, mock_openai_client):
    svc = EmbeddingService(settings=settings)
    svc._client = mock_openai_client
    return svc


def _make_embedding(dim: int = 1536) -> list[float]:
    return [0.01 * i for i in range(dim)]


class TestEmbedText:
    @pytest.mark.asyncio
    async def test_returns_embedding_vector(self, service, mock_openai_client):
        expected = _make_embedding()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=expected)]
        mock_openai_client.embeddings.create = AsyncMock(return_value=mock_response)

        result = await service.embed_text("organic cotton")

        assert result == expected
        assert len(result) == 1536

    @pytest.mark.asyncio
    async def test_calls_correct_model(self, service, mock_openai_client):
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=_make_embedding())]
        mock_openai_client.embeddings.create = AsyncMock(return_value=mock_response)

        await service.embed_text("silk")

        call_kwargs = mock_openai_client.embeddings.create.call_args
        assert call_kwargs.kwargs["model"] == "openai/text-embedding-3-small"


class TestEmbedBatch:
    @pytest.mark.asyncio
    async def test_returns_multiple_vectors(self, service, mock_openai_client):
        embeddings = [_make_embedding(), _make_embedding()]
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in embeddings]
        mock_openai_client.embeddings.create = AsyncMock(return_value=mock_response)

        result = await service.embed_batch(["cotton", "silk"])

        assert len(result) == 2
        assert all(len(v) == 1536 for v in result)
