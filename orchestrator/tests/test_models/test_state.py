"""Tests for LangGraph state definition."""

from typing import get_type_hints

from app.models.bom import BOMItem
from app.models.brief import DesignBrief, GarmentType
from app.models.fabric import FabricSpec
from app.models.measurements import Measurements
from app.models.state import TechPackState
from app.models.techpack import ConstructionDetail, TechPack


class TestTechPackState:
    def test_is_typed_dict(self):
        assert hasattr(TechPackState, "__annotations__")

    def test_has_all_expected_keys(self):
        expected_keys = {
            "brief",
            "garment_type",
            "measurements",
            "fabrics",
            "bom",
            "construction",
            "tech_pack",
            "current_agent",
            "agent_messages",
            "errors",
            "retry_count",
        }
        assert set(TechPackState.__annotations__.keys()) == expected_keys

    def test_type_hints_are_correct(self):
        hints = get_type_hints(TechPackState)
        assert hints["brief"] is DesignBrief
        assert hints["current_agent"] is str
        assert hints["retry_count"] is int

    def test_can_instantiate(self):
        state: TechPackState = {
            "brief": DesignBrief(description="test"),
            "garment_type": GarmentType.TOP,
            "measurements": None,
            "fabrics": [],
            "bom": [],
            "construction": [],
            "tech_pack": None,
            "current_agent": "brief_analyzer",
            "agent_messages": [],
            "errors": [],
            "retry_count": 0,
        }
        assert state["current_agent"] == "brief_analyzer"
        assert state["retry_count"] == 0
        assert state["garment_type"] == GarmentType.TOP
