"""Tech pack domain models."""

from pydantic import BaseModel, Field

from .bom import BOMItem
from .brief import DesignBrief
from .fabric import FabricSpec
from .measurements import Measurements


class ConstructionDetail(BaseModel):
    """Assembly instructions."""

    step: int = Field(..., ge=1)
    description: str = Field(..., min_length=1)
    stitch_type: str | None = None
    seam_allowance: str | None = None


class TechPack(BaseModel):
    """Final output — assembled by tech_pack_writer agent."""

    id: str = Field(..., min_length=1)
    brief: DesignBrief
    measurements: Measurements
    primary_fabric: FabricSpec
    secondary_fabrics: list[FabricSpec] = []
    bom: list[BOMItem]
    construction: list[ConstructionDetail]
    colorways: list[dict[str, str]] = []
    status: str = "draft"
    created_at: str = Field(..., min_length=1)
    version: int = 1
