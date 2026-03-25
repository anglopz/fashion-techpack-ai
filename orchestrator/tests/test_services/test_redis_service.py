"""Tests for the Redis service with mocked redis client."""

import json
from unittest.mock import AsyncMock

import pytest

from app.services.redis_service import RedisService


@pytest.fixture
def mock_redis():
    client = AsyncMock()
    return client


@pytest.fixture
def service(mock_redis):
    svc = RedisService(client=mock_redis)
    return svc


class TestGet:
    @pytest.mark.asyncio
    async def test_returns_deserialized_json(self, service, mock_redis):
        mock_redis.get = AsyncMock(return_value=json.dumps({"key": "value"}))
        result = await service.get("test-key")
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_key(self, service, mock_redis):
        mock_redis.get = AsyncMock(return_value=None)
        result = await service.get("missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_plain_string(self, service, mock_redis):
        mock_redis.get = AsyncMock(return_value="plain-string")
        result = await service.get("str-key")
        assert result == "plain-string"


class TestSet:
    @pytest.mark.asyncio
    async def test_set_with_ttl(self, service, mock_redis):
        await service.set("key", {"data": 1}, ttl=300)
        mock_redis.setex.assert_awaited_once_with("key", 300, json.dumps({"data": 1}))

    @pytest.mark.asyncio
    async def test_set_without_ttl(self, service, mock_redis):
        await service.set("key", {"data": 1})
        mock_redis.set.assert_awaited_once_with("key", json.dumps({"data": 1}))

    @pytest.mark.asyncio
    async def test_set_plain_string(self, service, mock_redis):
        await service.set("key", "hello")
        mock_redis.set.assert_awaited_once_with("key", "hello")


class TestDelete:
    @pytest.mark.asyncio
    async def test_deletes_key(self, service, mock_redis):
        await service.delete("key")
        mock_redis.delete.assert_awaited_once_with("key")


class TestConnectionGuard:
    @pytest.mark.asyncio
    async def test_raises_when_not_connected(self):
        svc = RedisService()
        with pytest.raises(RuntimeError, match="not connected"):
            await svc.get("key")
