"""Measurement domain models."""

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .brief import GarmentType


def _parse_measurement(value: Any) -> float:
    """Parse a measurement value, stripping unit suffixes like 'cm', 'in'."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[a-zA-Z\s]+$", "", value.strip())
        return float(cleaned)
    return float(value)


class Measurements(BaseModel):
    """Extracted by spec_extractor agent."""

    garment_type: GarmentType
    size_range: str = Field(..., min_length=1)
    key_measurements: dict[str, dict[str, float]]
    fit_type: str = Field(..., min_length=1)
    notes: list[str] = []

    @field_validator("size_range", mode="before")
    @classmethod
    def coerce_size_range(cls, v: Any) -> str:
        """LLMs sometimes return size_range as a list — join to string."""
        if isinstance(v, list):
            return "-".join(str(s) for s in [v[0], v[-1]]) if v else "OS"
        return v

    @field_validator("key_measurements", mode="before")
    @classmethod
    def coerce_measurements(cls, v: Any) -> dict[str, dict[str, float]]:
        """Strip unit suffixes (e.g. '102cm' -> 102.0) from LLM output."""
        if not isinstance(v, dict):
            return v
        return {
            size: {
                dim: _parse_measurement(val)
                for dim, val in dims.items()
            }
            for size, dims in v.items()
            if isinstance(dims, dict)
        }

    @field_validator("notes", mode="before")
    @classmethod
    def coerce_notes(cls, v: Any) -> list[str]:
        """LLMs sometimes return notes as a dict — coerce to list."""
        if isinstance(v, dict):
            return [f"{k}: {val}" for k, val in v.items()]
        if isinstance(v, str):
            return [v]
        return v
