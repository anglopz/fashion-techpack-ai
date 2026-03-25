"""Bill of Materials domain models."""

from pydantic import BaseModel, Field


class BOMItem(BaseModel):
    """Bill of Materials item from bom_builder agent."""

    category: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    quantity: str = Field(..., min_length=1)
    unit: str = Field(..., min_length=1)
    color: str | None = None
    supplier: str | None = None
