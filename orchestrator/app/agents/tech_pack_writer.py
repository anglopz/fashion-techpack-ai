"""Tech pack writer agent node — assembles final tech pack from all state data."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel

from app.models.fabric import FabricSpec
from app.models.state import TechPackState
from app.models.techpack import ConstructionDetail, TechPack
from app.services.llm_client import LLMClient

SYSTEM_PROMPT = """You are a fashion tech pack writer. Generate construction details for garment manufacturing.

For each construction step, specify:
- step: Sequential step number (1, 2, 3, ...)
- description: Detailed instruction
- stitch_type: e.g., lockstitch, overlock, coverstitch, flatlock, blindstitch
- seam_allowance: e.g., "1cm", "1.5cm", "0.5cm"

Also provide colorways as a list of dicts with color_name and hex_code.

Return a JSON object with 'construction' (array of steps) and 'colorways' (array of color dicts)."""


class WriterOutput(BaseModel):
    """Structured output from tech pack writer."""

    construction: list[ConstructionDetail]
    colorways: list[dict[str, str]] = []


async def tech_pack_writer_node(
    state: TechPackState,
    *,
    llm_client: LLMClient | None = None,
) -> dict:
    """Assemble the final tech pack with construction details.

    Uses task_type="reasoning" (claude-sonnet) for detailed construction specs.
    """
    llm = llm_client or LLMClient()
    brief = state["brief"]
    garment_type = state["garment_type"]
    fabrics = state["fabrics"]
    bom = state["bom"]

    fabric_info = ", ".join(f"{f.name} ({f.composition})" for f in fabrics) if fabrics else "TBD"
    bom_summary = ", ".join(f"{item.description}" for item in bom) if bom else "TBD"

    user_content = (
        f"Garment: {garment_type.value} - {brief.description}\n"
        f"Fabrics: {fabric_info}\n"
        f"BOM items: {bom_summary}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    writer_output: WriterOutput = await llm.structured_output(
        messages, task_type="reasoning", response_model=WriterOutput
    )

    # Assemble the complete TechPack
    tech_pack = TechPack(
        id=f"tp_{uuid.uuid4().hex[:12]}",
        brief=brief,
        measurements=state["measurements"],
        primary_fabric=fabrics[0] if fabrics else FabricSpec(
            name="TBD", composition="TBD", weight_gsm=0.1, width_cm=0.1, color="TBD"
        ),
        secondary_fabrics=fabrics[1:] if len(fabrics) > 1 else [],
        bom=bom,
        construction=writer_output.construction,
        colorways=writer_output.colorways,
        status="draft",
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    return {
        "tech_pack": tech_pack,
        "construction": writer_output.construction,
        "current_agent": "tech_pack_writer",
        "agent_messages": state["agent_messages"]
            + [{"agent": "tech_pack_writer", "content": "Tech pack assembled"}],
    }
