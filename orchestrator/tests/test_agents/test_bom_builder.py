"""Tests for bom_builder agent node."""

import pytest

from app.agents.bom_builder import BOMList, bom_builder_node
from app.models.bom import BOMItem
from app.models.brief import DesignBrief, GarmentType
from app.models.fabric import FabricSpec


def _make_state(**overrides) -> dict:
    base = {
        "brief": DesignBrief(description="Relaxed cotton t-shirt"),
        "garment_type": GarmentType.TOP,
        "measurements": None,
        "fabrics": [
            FabricSpec(
                name="Organic Jersey",
                composition="100% Organic Cotton",
                weight_gsm=180.0,
                width_cm=150.0,
                color="Navy",
            )
        ],
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
async def test_returns_bom_items(mocker):
    """Node returns a list of BOMItem instances."""
    mock_items = [
        BOMItem(category="fabric", description="Organic Jersey", quantity="1.5", unit="meters"),
        BOMItem(category="thread", description="Navy polyester thread", quantity="1", unit="spool"),
    ]
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=BOMList(items=mock_items)
    )

    state = _make_state()
    result = await bom_builder_node(state, llm_client=mock_llm)

    assert len(result["bom"]) == 2
    assert all(isinstance(item, BOMItem) for item in result["bom"])
    assert result["current_agent"] == "bom_builder"


@pytest.mark.asyncio
async def test_uses_extraction_task_type(mocker):
    """Verifies that task_type='extraction' is passed to structured_output."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=BOMList(items=[])
    )

    state = _make_state()
    await bom_builder_node(state, llm_client=mock_llm)

    call_args = mock_llm.structured_output.call_args
    assert call_args.kwargs.get("task_type") == "extraction" or call_args[0][1] == "extraction"


@pytest.mark.asyncio
async def test_includes_fabric_info_in_prompt(mocker):
    """Fabric names appear in the user message sent to the LLM."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=BOMList(items=[])
    )

    state = _make_state()
    await bom_builder_node(state, llm_client=mock_llm)

    messages = mock_llm.structured_output.call_args[0][0]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "Organic Jersey" in user_msg["content"]
