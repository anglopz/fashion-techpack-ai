"""Design brief domain models."""

from enum import Enum

from pydantic import BaseModel, Field


class GarmentType(str, Enum):
    """Supported garment categories."""

    TOP = "top"
    BOTTOM = "bottom"
    DRESS = "dress"
    OUTERWEAR = "outerwear"
    ACCESSORY = "accessory"


class DesignBrief(BaseModel):
    """Input from the designer."""

    description: str = Field(..., min_length=1)
    garment_type: GarmentType | None = None
    target_season: str | None = None
    style_references: list[str] = []
    fabric_preferences: list[str] = []
    color_palette: list[str] = []
