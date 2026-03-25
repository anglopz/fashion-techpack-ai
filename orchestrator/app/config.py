"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ModelRouting:
    """Maps task types to OpenRouter model identifiers."""

    reasoning: str = "anthropic/claude-sonnet-4"
    extraction: str = "openai/gpt-4o-mini"
    embedding: str = "openai/text-embedding-3-small"

    _task_map: dict[str, str] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        mapping = {
            "reasoning": self.reasoning,
            "extraction": self.extraction,
            "embedding": self.embedding,
        }
        object.__setattr__(self, "_task_map", mapping)

    def get_model(self, task_type: str) -> str:
        """Return the model name for a given task type."""
        if task_type not in self._task_map:
            raise ValueError(
                f"Unknown task_type '{task_type}'. "
                f"Valid types: {list(self._task_map.keys())}"
            )
        return self._task_map[task_type]


@dataclass(frozen=True)
class Settings:
    """Application settings sourced from environment variables."""

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Server
    orchestrator_port: int = 8000

    # Model routing
    models: ModelRouting = field(default_factory=ModelRouting)

    @staticmethod
    def from_env() -> Settings:
        """Build Settings from current environment variables."""
        return Settings(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_base_url=os.getenv(
                "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
            ),
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
            supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
            orchestrator_port=int(os.getenv("ORCHESTRATOR_PORT", "8000")),
            models=ModelRouting(
                reasoning=os.getenv(
                    "MODEL_REASONING", "anthropic/claude-sonnet-4"
                ),
                extraction=os.getenv("MODEL_EXTRACTION", "openai/gpt-4o-mini"),
                embedding=os.getenv(
                    "MODEL_EMBEDDING", "openai/text-embedding-3-small"
                ),
            ),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings.from_env()
