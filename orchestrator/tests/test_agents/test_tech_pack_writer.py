"""Tests for tech_pack_writer agent node."""

import pytest

from app.agents.tech_pack_writer import WriterOutput, tech_pack_writer_node
from app.models.bom import BOMItem
from app.models.brief import DesignBrief, GarmentType
from app.models.fabric import FabricSpec
from app.models.measurements import Measurements
from app.models.techpack import ConstructionDetail, TechPack


def _make_state(**overrides) -> dict:
    base = {
        "brief": DesignBrief(description="Relaxed cotton t-shirt"),
        "garment_type": GarmentType.TOP,
        "measurements": Measurements(
            garment_type=GarmentType.TOP,
            size_range="XS-XXL",
            key_measurements={"M": {"chest": 96.0}},
            fit_type="relaxed",
        ),
        "fabrics": [
            FabricSpec(
                name="Organic Jersey",
                composition="100% Organic Cotton",
                weight_gsm=180.0,
                width_cm=150.0,
                color="Navy",
            )
        ],
        "bom": [
            BOMItem(category="fabric", description="Organic Jersey", quantity="1.5", unit="meters"),
        ],
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
async def test_returns_complete_tech_pack(mocker):
    """Node returns a fully assembled TechPack."""
    mock_output = WriterOutput(
        construction=[
            ConstructionDetail(step=1, description="Cut fabric", stitch_type="N/A"),
            ConstructionDetail(step=2, description="Sew shoulder seams", stitch_type="overlock"),
        ],
        colorways=[{"color_name": "Navy", "hex_code": "#001F3F"}],
    )
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(return_value=mock_output)

    state = _make_state()
    result = await tech_pack_writer_node(state, llm_client=mock_llm)

    assert isinstance(result["tech_pack"], TechPack)
    assert result["tech_pack"].status == "draft"
    assert len(result["construction"]) == 2
    assert result["current_agent"] == "tech_pack_writer"


@pytest.mark.asyncio
async def test_uses_reasoning_task_type(mocker):
    """Verifies that task_type='reasoning' is passed to structured_output."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=WriterOutput(construction=[], colorways=[])
    )

    state = _make_state()
    await tech_pack_writer_node(state, llm_client=mock_llm)

    call_args = mock_llm.structured_output.call_args
    assert call_args.kwargs.get("task_type") == "reasoning" or call_args[0][1] == "reasoning"


@pytest.mark.asyncio
async def test_tech_pack_has_generated_id(mocker):
    """Tech pack ID starts with 'tp_' and has a hex suffix."""
    mock_llm = mocker.AsyncMock()
    mock_llm.structured_output = mocker.AsyncMock(
        return_value=WriterOutput(
            construction=[ConstructionDetail(step=1, description="Cut")],
            colorways=[],
        )
    )

    state = _make_state()
    result = await tech_pack_writer_node(state, llm_client=mock_llm)

    tp_id = result["tech_pack"].id
    assert tp_id.startswith("tp_")
    assert len(tp_id) == 15  # "tp_" + 12 hex chars
