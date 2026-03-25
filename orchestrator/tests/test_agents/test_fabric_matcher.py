"""Tests for fabric_matcher agent node."""

import json

import pytest

from app.agents.fabric_matcher import fabric_matcher_node
from app.models.brief import DesignBrief, GarmentType
from app.models.fabric import FabricSpec


def _make_state(**overrides) -> dict:
    base = {
        "brief": DesignBrief(
            description="Relaxed cotton t-shirt",
            fabric_preferences=["organic cotton"],
            target_season="SS26",
        ),
        "garment_type": GarmentType.TOP,
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
    base.update(overrides)
    return base


def _fake_fabric(name: str) -> dict:
    return {
        "name": name,
        "composition": "100% Cotton",
        "weight_gsm": 180.0,
        "width_cm": 150.0,
        "color": "Natural",
        "supplier": "TestMill",
        "similarity_score": 0.9,
    }


@pytest.mark.asyncio
async def test_returns_fabric_specs(mocker):
    """Node returns FabricSpec instances from RAG results."""
    mock_rag = mocker.AsyncMock()
    mock_rag.search_fabrics = mocker.AsyncMock(
        return_value=[_fake_fabric("Jersey A"), _fake_fabric("Jersey B"), _fake_fabric("Jersey C")]
    )
    mock_llm = mocker.AsyncMock()
    mock_llm.chat_completion = mocker.AsyncMock(
        return_value=json.dumps(["Jersey A", "Jersey C", "Jersey B"])
    )

    state = _make_state()
    result = await fabric_matcher_node(state, rag_service=mock_rag, llm_client=mock_llm)

    assert len(result["fabrics"]) == 3
    assert all(isinstance(f, FabricSpec) for f in result["fabrics"])
    assert result["current_agent"] == "fabric_matcher"


@pytest.mark.asyncio
async def test_builds_query_from_brief(mocker):
    """Search query includes garment type, fabric prefs, and season."""
    mock_rag = mocker.AsyncMock()
    mock_rag.search_fabrics = mocker.AsyncMock(return_value=[])
    mock_llm = mocker.AsyncMock()

    state = _make_state()
    await fabric_matcher_node(state, rag_service=mock_rag, llm_client=mock_llm)

    query = mock_rag.search_fabrics.call_args[0][0]
    assert "top" in query.lower()
    assert "organic cotton" in query.lower()
    assert "ss26" in query.lower()


@pytest.mark.asyncio
async def test_handles_empty_rag_results(mocker):
    """Returns empty fabrics list when RAG finds nothing."""
    mock_rag = mocker.AsyncMock()
    mock_rag.search_fabrics = mocker.AsyncMock(return_value=[])
    mock_llm = mocker.AsyncMock()

    state = _make_state()
    result = await fabric_matcher_node(state, rag_service=mock_rag, llm_client=mock_llm)

    assert result["fabrics"] == []
    # LLM should NOT be called when no candidates
    mock_llm.chat_completion.assert_not_called()
