"""LangGraph workflow for tech pack generation."""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents import (
    brief_analyzer_node,
    bom_builder_node,
    fabric_matcher_node,
    spec_extractor_node,
    tech_pack_writer_node,
)
from app.models import TechPackState


def validation_node(state: TechPackState) -> dict[str, Any]:
    """Validate the assembled tech pack for completeness."""
    errors: list[str] = []

    if state.get("tech_pack") is None:
        errors.append("tech_pack is missing")
    if not state.get("measurements"):
        errors.append("measurements are missing")
    if not state.get("fabrics"):
        errors.append("fabrics are missing")
    if not state.get("construction"):
        errors.append("construction details are missing")

    retry_count = state.get("retry_count", 0)
    if errors:
        retry_count += 1

    return {
        "errors": errors,
        "retry_count": retry_count,
        "current_agent": "validation",
        "agent_messages": [
            {
                "agent": "validation",
                "message": "Validation passed" if not errors else f"Validation failed: {errors}",
            }
        ],
    }


def _should_retry(state: TechPackState) -> str:
    """Decide whether to retry the tech pack writer or finish."""
    if state.get("errors") and state.get("retry_count", 0) < 2:
        return "retry"
    return "end"


def build_techpack_graph(*, checkpointer: Any = None) -> CompiledStateGraph:
    """Build and compile the tech pack generation StateGraph."""
    graph = StateGraph(TechPackState)

    # Add nodes
    graph.add_node("brief_analyzer", brief_analyzer_node)
    graph.add_node("spec_extractor", spec_extractor_node)
    graph.add_node("fabric_matcher", fabric_matcher_node)
    graph.add_node("bom_builder", bom_builder_node)
    graph.add_node("tech_pack_writer", tech_pack_writer_node)
    graph.add_node("validation", validation_node)

    # Linear edges
    graph.set_entry_point("brief_analyzer")
    graph.add_edge("brief_analyzer", "spec_extractor")
    graph.add_edge("spec_extractor", "fabric_matcher")
    graph.add_edge("fabric_matcher", "bom_builder")
    graph.add_edge("bom_builder", "tech_pack_writer")
    graph.add_edge("tech_pack_writer", "validation")

    # Conditional retry from validation
    graph.add_conditional_edges(
        "validation",
        _should_retry,
        {"retry": "tech_pack_writer", "end": END},
    )

    return graph.compile(checkpointer=checkpointer or MemorySaver())
