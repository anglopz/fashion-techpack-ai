"""Spec extractor agent node — generates measurements from garment type and brief."""

from __future__ import annotations

from app.models.measurements import Measurements
from app.models.state import TechPackState
from app.services.llm_client import LLMClient

SYSTEM_PROMPT = """You are a fashion technical specification expert. Generate measurement specifications.

Standard measurement tables by garment type:

TOPS (t-shirts, blouses, shirts):
- chest, shoulder_width, sleeve_length, body_length, hem_width
- Size range: XS-XXL

BOTTOMS (trousers, skirts, shorts):
- waist, hip, inseam, outseam, thigh, knee, leg_opening
- Size range: XS-XXL

DRESSES (dresses, jumpsuits):
- bust, waist, hip, shoulder_width, body_length, sleeve_length
- Size range: XS-XXL

OUTERWEAR (jackets, coats):
- chest, shoulder_width, sleeve_length, body_length, hem_width
- Size range: XS-XXL (with ease allowance)

Return measurements as a JSON object with garment_type, size_range, key_measurements (dict of size -> measurement dict), fit_type, and notes."""


async def spec_extractor_node(
    state: TechPackState,
    *,
    llm_client: LLMClient | None = None,
) -> dict:
    """Extract measurement specifications using reasoning model.

    Uses task_type="reasoning" (claude-sonnet) for detailed spec generation.
    """
    llm = llm_client or LLMClient()
    brief = state["brief"]
    garment_type = state["garment_type"]

    style_keywords = ", ".join(brief.fabric_preferences) if brief.fabric_preferences else "standard"

    user_content = (
        f"Garment type: {garment_type.value}\n"
        f"Description: {brief.description}\n"
        f"Style keywords: {style_keywords}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    measurements: Measurements = await llm.structured_output(
        messages, task_type="reasoning", response_model=Measurements
    )

    return {
        "measurements": measurements,
        "current_agent": "spec_extractor",
        "agent_messages": state["agent_messages"]
            + [{"agent": "spec_extractor", "content": f"Generated measurements for {garment_type.value}"}],
    }
