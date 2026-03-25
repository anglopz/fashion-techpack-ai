"""Tests for brief_analyzer agent node."""

import pytest

from app.agents.brief_analyzer import BriefAnalysis, brief_analyzer_node
from app.models.brief import DesignBrief, GarmentType


def _make_state(brief: DesignBrief, **overrides) -> dict:
    """Create a minimal TechPackState dict for testing."""
    base = {
        "brief": brief,
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
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_detects_garment_type(mocker):
    """LLM-detected garment type is returned when brief has no explicit type."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=BriefAnalysis(
            garment_type=GarmentType.TOP,
            keywords=["relaxed-fit", "organic cotton"],
            color_palette=["navy", "cream"],
        )
    )

    brief = DesignBrief(description="Relaxed-fit organic cotton t-shirt in navy and cream")
    state = _make_state(brief)

    result = await brief_analyzer_node(state, llm_client=mock_llm)

    assert result["garment_type"] == GarmentType.TOP
    assert result["current_agent"] == "brief_analyzer"


@pytest.mark.asyncio
async def test_preserves_explicit_garment_type(mocker):
    """Explicit garment type from brief overrides LLM detection."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=BriefAnalysis(
            garment_type=GarmentType.TOP,
            keywords=["oversized"],
            color_palette=["black"],
        )
    )

    brief = DesignBrief(
        description="Oversized puffer jacket",
        garment_type=GarmentType.OUTERWEAR,
    )
    state = _make_state(brief)

    result = await brief_analyzer_node(state, llm_client=mock_llm)

    assert result["garment_type"] == GarmentType.OUTERWEAR


@pytest.mark.asyncio
async def test_extracts_color_palette(mocker):
    """Extracted colors are merged into the brief."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=BriefAnalysis(
            garment_type=GarmentType.DRESS,
            keywords=["floral"],
            color_palette=["rose", "sage"],
        )
    )

    brief = DesignBrief(
        description="Floral midi dress",
        color_palette=["ivory"],
    )
    state = _make_state(brief)

    result = await brief_analyzer_node(state, llm_client=mock_llm)

    palette = result["brief"].color_palette
    assert "ivory" in palette
    assert "rose" in palette
    assert "sage" in palette


@pytest.mark.asyncio
async def test_uses_extraction_task_type(mocker):
    """Verifies that task_type='extraction' is passed to structured_output."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=BriefAnalysis(
            garment_type=GarmentType.TOP,
            keywords=[],
            color_palette=[],
        )
    )

    brief = DesignBrief(description="Basic tee")
    state = _make_state(brief)

    await brief_analyzer_node(state, llm_client=mock_llm)

    call_args = mock_llm.structured_output.call_args
    assert call_args.kwargs.get("task_type") == "extraction" or call_args[0][1] == "extraction"
