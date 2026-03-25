"""Measurement domain models."""

from pydantic import BaseModel, Field

from .brief import GarmentType


class Measurements(BaseModel):
    """Extracted by spec_extractor agent."""

    garment_type: GarmentType
    size_range: str = Field(..., min_length=1)
    key_measurements: dict[str, dict[str, float]]
    fit_type: str = Field(..., min_length=1)
    notes: list[str] = []
