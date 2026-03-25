"""RAG service for fabric catalog search using Supabase pgvector."""

from __future__ import annotations

from supabase import AsyncClient as SupabaseClient
from supabase import acreate_client

from app.config import Settings, get_settings
from app.services.embedding_service import EmbeddingService


class RAGService:
    """Semantic search over the fabric catalog via pgvector."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        supabase_client: SupabaseClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._embedding_service = embedding_service or EmbeddingService(self._settings)
        self._supabase = supabase_client
        self._table = "fabrics"

    async def _get_client(self) -> SupabaseClient:
        """Lazy-init the Supabase async client."""
        if self._supabase is None:
            self._supabase = await acreate_client(
                self._settings.supabase_url,
                self._settings.supabase_service_key,
            )
        return self._supabase

    async def search_fabrics(
        self, query: str, limit: int = 5
    ) -> list[dict]:
        """Search fabrics by semantic similarity.

        Pipeline: query → embed → pgvector cosine search → ranked results.
        """
        query_embedding = await self._embedding_service.embed_text(query)
        client = await self._get_client()

        # Uses the Supabase RPC call for vector similarity search
        response = await client.rpc(
            "match_fabrics",
            {
                "query_embedding": query_embedding,
                "match_count": limit,
            },
        ).execute()

        return response.data or []
