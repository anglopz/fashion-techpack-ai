"""Fabric specification domain models."""

from pydantic import BaseModel, Field


class FabricSpec(BaseModel):
    """Matched by fabric_matcher agent (from RAG)."""

    name: str = Field(..., min_length=1)
    composition: str = Field(..., min_length=1)
    weight_gsm: float = Field(..., gt=0)
    width_cm: float = Field(..., gt=0)
    color: str = Field(..., min_length=1)
    supplier: str | None = None
    price_per_meter: float | None = None
    care_instructions: list[str] = []
    similarity_score: float = 0.0
