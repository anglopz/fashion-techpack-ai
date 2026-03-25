"""Fabric matcher agent node — RAG search + LLM rerank for fabric selection."""

from __future__ import annotations

from app.models.fabric import FabricSpec
from app.models.state import TechPackState
from app.services.llm_client import LLMClient
from app.services.rag_service import RAGService


async def fabric_matcher_node(
    state: TechPackState,
    *,
    rag_service: RAGService | None = None,
    llm_client: LLMClient | None = None,
) -> dict:
    """Match fabrics using vector search and LLM reranking.

    Pipeline: build query -> RAG search -> LLM rerank -> top 3 FabricSpec.
    """
    import json

    rag = rag_service or RAGService()
    llm = llm_client or LLMClient()
    brief = state["brief"]
    garment_type = state["garment_type"]

    # Build search query from context
    query_parts = [garment_type.value]
    if brief.fabric_preferences:
        query_parts.extend(brief.fabric_preferences)
    if brief.target_season:
        query_parts.append(brief.target_season)
    query = " ".join(query_parts)

    # Vector search
    candidates = await rag.search_fabrics(query, limit=5)

    if not candidates:
        return {
            "fabrics": [],
            "current_agent": "fabric_matcher",
            "agent_messages": state["agent_messages"]
                + [{"agent": "fabric_matcher", "content": "No fabrics found in catalog"}],
        }

    # LLM rerank
    candidate_names = [c.get("name", f"fabric_{i}") for i, c in enumerate(candidates)]
    rerank_messages = [
        {
            "role": "system",
            "content": (
                "You are a fabric selection expert. Rank these fabrics by suitability "
                "for the given garment. Return a JSON array of fabric names in order "
                "from most to least suitable."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Garment: {garment_type.value} - {brief.description}\n"
                f"Candidates: {json.dumps(candidate_names)}"
            ),
        },
    ]

    rerank_response = await llm.chat_completion(
        rerank_messages, task_type="extraction"
    )

    # Parse reranked order
    try:
        ranked_names = json.loads(rerank_response)
        # Reorder candidates by ranked names
        name_to_candidate = {c.get("name", f"fabric_{i}"): c for i, c in enumerate(candidates)}
        reranked = [name_to_candidate[n] for n in ranked_names if n in name_to_candidate]
        # Fall back to original order for any not in rerank
        reranked.extend(c for c in candidates if c not in reranked)
        candidates = reranked
    except (json.JSONDecodeError, KeyError):
        pass  # Keep original order if rerank fails

    # Convert top 3 to FabricSpec
    fabrics = []
    for candidate in candidates[:3]:
        fabrics.append(
            FabricSpec(
                name=candidate.get("name", "Unknown"),
                composition=candidate.get("composition", "Unknown"),
                weight_gsm=candidate.get("weight_gsm", 0.1),
                width_cm=candidate.get("width_cm", 0.1),
                color=candidate.get("color", "Natural"),
                supplier=candidate.get("supplier"),
                price_per_meter=candidate.get("price_per_meter"),
                care_instructions=candidate.get("care_instructions", []),
                similarity_score=candidate.get("similarity_score", 0.0),
            )
        )

    return {
        "fabrics": fabrics,
        "current_agent": "fabric_matcher",
        "agent_messages": state["agent_messages"]
            + [{"agent": "fabric_matcher", "content": f"Matched {len(fabrics)} fabrics"}],
    }
