"""Bill of Materials domain models."""

from pydantic import BaseModel, Field, field_validator


class BOMItem(BaseModel):
    """Bill of Materials item from bom_builder agent."""

    category: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    quantity: str = Field(..., min_length=1)
    unit: str = Field(default="pcs")
    color: str | None = None
    supplier: str | None = None

    @field_validator("unit", mode="before")
    @classmethod
    def default_empty_unit(cls, v: str) -> str:
        if not v or not v.strip():
            return "pcs"
        return v
