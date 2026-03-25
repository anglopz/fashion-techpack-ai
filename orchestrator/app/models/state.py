"""LangGraph state definition."""

from typing import TypedDict

from .bom import BOMItem
from .brief import DesignBrief, GarmentType
from .fabric import FabricSpec
from .measurements import Measurements
from .techpack import ConstructionDetail, TechPack


class TechPackState(TypedDict):
    """State that flows through the LangGraph."""

    brief: DesignBrief
    garment_type: GarmentType | None
    measurements: Measurements | None
    fabrics: list[FabricSpec]
    bom: list[BOMItem]
    construction: list[ConstructionDetail]
    tech_pack: TechPack | None
    current_agent: str
    agent_messages: list[dict]
    errors: list[str]
    retry_count: int
