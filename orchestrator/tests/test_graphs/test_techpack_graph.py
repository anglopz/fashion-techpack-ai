"""Tests for the LangGraph tech pack workflow."""

from __future__ import annotations

import pytest

from app.graphs.techpack_graph import build_techpack_graph, validation_node
from app.models import DesignBrief, TechPackState


def _make_state(**overrides) -> TechPackState:
    """Build a minimal TechPackState with sensible defaults."""
    base: TechPackState = {
        "brief": DesignBrief(description="Test brief"),
        "garment_type": None,
        "measurements": None,
        "fabrics": [],
        "bom": [],
        "construction": [],
        "tech_pack": None,
        "current_agent": "",
        "agent_messages": [],
        "errors": [],
        "retry_count": 0,
    }
    base.update(overrides)  # type: ignore[typeddict-item]
    return base


class TestBuildGraph:
    """Verify that the graph compiles and has the correct structure."""

    def test_graph_compiles(self) -> None:
        graph = build_techpack_graph()
        assert graph is not None

    def test_graph_has_all_nodes(self) -> None:
        graph = build_techpack_graph()
        node_names = set(graph.get_graph().nodes.keys()) - {"__start__", "__end__"}
        expected = {
            "brief_analyzer",
            "spec_extractor",
            "fabric_matcher",
            "bom_builder",
            "tech_pack_writer",
            "validation",
        }
        assert node_names == expected


class TestValidationNode:
    """Unit tests for the synchronous validation node."""

    def test_valid_techpack_passes(self) -> None:
        state = _make_state(
            tech_pack={"id": "tp_1"},
            measurements={"bust": 90},
            fabrics=[{"name": "cotton"}],
            construction=[{"step": 1, "description": "sew"}],
        )
        result = validation_node(state)
        assert result["errors"] == []
        assert result["retry_count"] == 0

    def test_missing_techpack_fails(self) -> None:
        state = _make_state(tech_pack=None)
        result = validation_node(state)
        assert len(result["errors"]) > 0
        assert any("tech_pack" in e for e in result["errors"])

    def test_retry_count_increments(self) -> None:
        state = _make_state(tech_pack=None, retry_count=1)
        result = validation_node(state)
        assert result["retry_count"] == 2
