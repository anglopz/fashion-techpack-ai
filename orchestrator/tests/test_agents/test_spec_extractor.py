"""Tests for spec_extractor agent node."""

import pytest

from app.agents.spec_extractor import spec_extractor_node
from app.models.brief import DesignBrief, GarmentType
from app.models.measurements import Measurements


def _make_state(**overrides) -> dict:
    base = {
        "brief": DesignBrief(description="Relaxed-fit cotton t-shirt"),
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


@pytest.mark.asyncio
async def test_returns_measurements(mocker):
    """Node returns a Measurements instance."""
    mock_measurements = Measurements(
        garment_type=GarmentType.TOP,
        size_range="XS-XXL",
        key_measurements={"M": {"chest": 96.0, "body_length": 72.0}},
        fit_type="relaxed",
    )
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(return_value=mock_measurements)

    state = _make_state()
    result = await spec_extractor_node(state, llm_client=mock_llm)

    assert isinstance(result["measurements"], Measurements)
    assert result["measurements"].garment_type == GarmentType.TOP
    assert result["current_agent"] == "spec_extractor"


@pytest.mark.asyncio
async def test_uses_reasoning_task_type(mocker):
    """Verifies that task_type='reasoning' is passed to structured_output."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=Measurements(
            garment_type=GarmentType.TOP,
            size_range="XS-XXL",
            key_measurements={"M": {"chest": 96.0}},
            fit_type="relaxed",
        )
    )

    state = _make_state()
    await spec_extractor_node(state, llm_client=mock_llm)

    call_args = mock_llm.structured_output.call_args
    assert call_args.kwargs.get("task_type") == "reasoning" or call_args[0][1] == "reasoning"


@pytest.mark.asyncio
async def test_includes_garment_type_in_prompt(mocker):
    """Garment type appears in the user message sent to the LLM."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=Measurements(
            garment_type=GarmentType.BOTTOM,
            size_range="XS-XXL",
            key_measurements={"M": {"waist": 80.0}},
            fit_type="slim",
        )
    )

    state = _make_state(garment_type=GarmentType.BOTTOM)
    await spec_extractor_node(state, llm_client=mock_llm)

    messages = mock_llm.structured_output.call_args[0][0]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "bottom" in user_msg["content"].lower()
