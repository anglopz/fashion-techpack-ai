"""BOM builder agent node — generates bill of materials from garment specs."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.bom import BOMItem
from app.models.state import TechPackState
from app.services.llm_client import LLMClient

SYSTEM_PROMPT = """You are a fashion bill of materials specialist. Generate a complete BOM for garment production.

BOM categories:
- fabric: Main and secondary fabrics with yardage
- trim: Zippers, buttons, elastic, ribbons, etc.
- hardware: Snaps, grommets, buckles, etc.
- thread: Matching and contrast threads
- label: Brand labels, care labels, size labels

Return a JSON object with an 'items' array, where each item has:
category, description, quantity, unit, color (optional), supplier (optional)."""


class BOMList(BaseModel):
    """Structured output for BOM generation."""

    items: list[BOMItem]


async def bom_builder_node(
    state: TechPackState,
    *,
    llm_client: LLMClient | None = None,
) -> dict:
    """Generate a bill of materials for the garment.

    Uses task_type="extraction" (gpt-4o-mini) for structured BOM output.
    """
    llm = llm_client or LLMClient()
    garment_type = state["garment_type"]
    fabrics = state["fabrics"]

    fabric_info = ", ".join(f.name for f in fabrics) if fabrics else "not yet selected"

    user_content = (
        f"Garment type: {garment_type.value}\n"
        f"Fabrics: {fabric_info}\n"
        f"Description: {state['brief'].description}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    bom_list: BOMList = await llm.structured_output(
        messages, task_type="extraction", response_model=BOMList
    )

    return {
        "bom": bom_list.items,
        "current_agent": "bom_builder",
        "agent_messages": state["agent_messages"]
            + [{"agent": "bom_builder", "content": f"Generated BOM with {len(bom_list.items)} items"}],
    }
