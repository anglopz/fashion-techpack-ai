"""Tests for application configuration."""

import os
from unittest.mock import patch

from app.config import ModelRouting, Settings


class TestModelRouting:
    def test_get_model_reasoning(self):
        routing = ModelRouting()
        assert routing.get_model("reasoning") == "anthropic/claude-sonnet-4"

    def test_get_model_extraction(self):
        routing = ModelRouting()
        assert routing.get_model("extraction") == "openai/gpt-4o-mini"

    def test_get_model_embedding(self):
        routing = ModelRouting()
        assert routing.get_model("embedding") == "openai/text-embedding-3-small"

    def test_get_model_invalid_task_type(self):
        routing = ModelRouting()
        try:
            routing.get_model("nonexistent")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "nonexistent" in str(e)

    def test_custom_model_routing(self):
        routing = ModelRouting(reasoning="custom/model")
        assert routing.get_model("reasoning") == "custom/model"


class TestSettings:
    def test_from_env_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env()
            assert settings.openrouter_base_url == "https://openrouter.ai/api/v1"
            assert settings.redis_url == "redis://localhost:6379"
            assert settings.orchestrator_port == 8000

    def test_from_env_custom(self):
        env = {
            "OPENROUTER_API_KEY": "test-key",
            "SUPABASE_URL": "https://test.supabase.co",
            "REDIS_URL": "redis://custom:6380",
            "ORCHESTRATOR_PORT": "9000",
            "MODEL_REASONING": "custom/reasoning-model",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()
            assert settings.openrouter_api_key == "test-key"
            assert settings.supabase_url == "https://test.supabase.co"
            assert settings.redis_url == "redis://custom:6380"
            assert settings.orchestrator_port == 9000
            assert settings.models.get_model("reasoning") == "custom/reasoning-model"
