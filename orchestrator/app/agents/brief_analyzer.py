"""Brief analyzer agent node — parses design briefs into structured data."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.brief import GarmentType
from app.models.state import TechPackState
from app.services.llm_client import LLMClient

SYSTEM_PROMPT = """You are a fashion design brief analyst. Parse design briefs into structured data.

Extract the garment type, descriptive keywords, and color palette from the brief.

Examples:

Brief: "Relaxed-fit organic cotton t-shirt for SS26 in navy and cream"
Result: garment_type=top, keywords=["relaxed-fit", "organic cotton", "SS26"], color_palette=["navy", "cream"]

Brief: "Slim-fit wool trousers in charcoal with satin waistband"
Result: garment_type=bottom, keywords=["slim-fit", "wool", "satin waistband"], color_palette=["charcoal"]

Brief: "Oversized puffer jacket in black and olive for FW26"
Result: garment_type=outerwear, keywords=["oversized", "puffer", "FW26"], color_palette=["black", "olive"]

Return a JSON object with garment_type, keywords, and color_palette."""


class BriefAnalysis(BaseModel):
    """Structured output from brief analysis."""

    garment_type: GarmentType
    keywords: list[str] = Field(default_factory=list)
    color_palette: list[str] = Field(default_factory=list)


async def brief_analyzer_node(
    state: TechPackState,
    *,
    llm_client: LLMClient | None = None,
) -> dict:
    """Analyze a design brief and extract structured information.

    Uses task_type="extraction" (gpt-4o-mini) for fast parsing.
    """
    llm = llm_client or LLMClient()
    brief = state["brief"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": brief.description},
    ]

    analysis: BriefAnalysis = await llm.structured_output(
        messages, task_type="extraction", response_model=BriefAnalysis
    )

    # Use explicit garment_type from brief if provided, else use LLM detection
    garment_type = brief.garment_type if brief.garment_type is not None else analysis.garment_type

    # Merge extracted data into brief (don't overwrite existing values)
    updated_brief = brief.model_copy(
        update={
            "color_palette": list(set(brief.color_palette + analysis.color_palette)),
            "fabric_preferences": list(
                set(brief.fabric_preferences + [kw for kw in analysis.keywords if kw])
            ),
        }
    )

    return {
        "brief": updated_brief,
        "garment_type": garment_type,
        "current_agent": "brief_analyzer",
        "agent_messages": state["agent_messages"]
            + [{"agent": "brief_analyzer", "content": f"Detected garment type: {garment_type.value}"}],
    }
