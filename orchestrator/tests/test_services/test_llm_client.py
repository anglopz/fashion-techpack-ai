"""Tests for the LLM client with mocked OpenAI SDK."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from app.config import Settings
from app.services.llm_client import LLMClient


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
def llm_client(settings, mock_openai_client):
    client = LLMClient(settings=settings)
    client._client = mock_openai_client
    return client


class TestChatCompletion:
    @pytest.mark.asyncio
    async def test_routes_to_correct_model_reasoning(self, llm_client, mock_openai_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello"))]
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await llm_client.chat_completion(
            messages=[{"role": "user", "content": "Hi"}],
            task_type="reasoning",
        )

        assert result == "Hello"
        call_kwargs = mock_openai_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "anthropic/claude-sonnet-4"

    @pytest.mark.asyncio
    async def test_routes_to_correct_model_extraction(self, llm_client, mock_openai_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="data"))]
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        await llm_client.chat_completion(
            messages=[{"role": "user", "content": "extract"}],
            task_type="extraction",
        )

        call_kwargs = mock_openai_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "openai/gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_invalid_task_type_raises(self, llm_client):
        with pytest.raises(ValueError, match="Unknown task_type"):
            await llm_client.chat_completion(
                messages=[{"role": "user", "content": "test"}],
                task_type="invalid",
            )


class TestStructuredOutput:
    @pytest.mark.asyncio
    async def test_parses_response_model(self, llm_client, mock_openai_client):
        class TestModel(BaseModel):
            name: str
            value: int

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"name": "test", "value": 42}'))
        ]
        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await llm_client.structured_output(
            messages=[{"role": "user", "content": "give data"}],
            task_type="extraction",
            response_model=TestModel,
        )

        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42
