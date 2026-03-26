"""Measurement domain models."""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .brief import GarmentType


class Measurements(BaseModel):
    """Extracted by spec_extractor agent."""

    garment_type: GarmentType
    size_range: str = Field(..., min_length=1)
    key_measurements: dict[str, dict[str, float]]
    fit_type: str = Field(..., min_length=1)
    notes: list[str] = []

    @field_validator("notes", mode="before")
    @classmethod
    def coerce_notes(cls, v: Any) -> list[str]:
        """LLMs sometimes return notes as a dict — coerce to list."""
        if isinstance(v, dict):
            return [f"{k}: {val}" for k, val in v.items()]
        if isinstance(v, str):
            return [v]
        return v
