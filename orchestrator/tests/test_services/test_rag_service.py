"""Tests for the RAG service with mocked Supabase and embedding service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import Settings
from app.services.rag_service import RAGService


@pytest.fixture
def settings():
    return Settings(
        supabase_url="https://test.supabase.co",
        supabase_service_key="test-service-key",
    )


@pytest.fixture
def mock_embedding_service():
    svc = AsyncMock()
    svc.embed_text = AsyncMock(return_value=[0.1] * 1536)
    return svc


@pytest.fixture
def mock_supabase_client():
    client = AsyncMock()
    return client


@pytest.fixture
def service(settings, mock_embedding_service, mock_supabase_client):
    svc = RAGService(
        embedding_service=mock_embedding_service,
        supabase_client=mock_supabase_client,
        settings=settings,
    )
    return svc


class TestSearchFabrics:
    @pytest.mark.asyncio
    async def test_returns_matched_fabrics(
        self, service, mock_embedding_service, mock_supabase_client
    ):
        expected_results = [
            {"id": "1", "name": "Organic Cotton", "similarity": 0.95},
            {"id": "2", "name": "Silk Blend", "similarity": 0.87},
        ]
        # Chain: client.rpc(...).execute() -> response.data
        mock_execute = AsyncMock()
        mock_execute.execute = AsyncMock(
            return_value=MagicMock(data=expected_results)
        )
        mock_supabase_client.rpc = MagicMock(return_value=mock_execute)

        results = await service.search_fabrics("soft organic fabric")

        assert len(results) == 2
        assert results[0]["name"] == "Organic Cotton"
        mock_embedding_service.embed_text.assert_awaited_once_with(
            "soft organic fabric"
        )

    @pytest.mark.asyncio
    async def test_respects_limit(
        self, service, mock_embedding_service, mock_supabase_client
    ):
        mock_execute = AsyncMock()
        mock_execute.execute = AsyncMock(return_value=MagicMock(data=[]))
        mock_supabase_client.rpc = MagicMock(return_value=mock_execute)

        await service.search_fabrics("cotton", limit=3)

        call_args = mock_supabase_client.rpc.call_args
        assert call_args.args[1]["match_count"] == 3

    @pytest.mark.asyncio
    async def test_returns_empty_on_no_results(
        self, service, mock_supabase_client
    ):
        mock_execute = AsyncMock()
        mock_execute.execute = AsyncMock(return_value=MagicMock(data=None))
        mock_supabase_client.rpc = MagicMock(return_value=mock_execute)

        results = await service.search_fabrics("nonexistent fabric")

        assert results == []
