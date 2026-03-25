"""Redis caching service with JSON serialization."""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from app.config import Settings, get_settings


class RedisService:
    """Async Redis client wrapper for caching."""

    def __init__(
        self,
        client: aioredis.Redis | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client

    async def connect(self) -> None:
        """Initialize the Redis connection."""
        if self._client is None:
            self._client = aioredis.from_url(
                self._settings.redis_url,
                decode_responses=True,
            )

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _ensure_connected(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("RedisService not connected. Call connect() first.")
        return self._client

    async def get(self, key: str) -> Any | None:
        """Get a value by key, deserializing JSON if needed."""
        client = self._ensure_connected()
        value = await client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a key to a value with optional TTL in seconds."""
        client = self._ensure_connected()
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl is not None:
            await client.setex(key, ttl, serialized)
        else:
            await client.set(key, serialized)

    async def delete(self, key: str) -> None:
        """Delete a key."""
        client = self._ensure_connected()
        await client.delete(key)
