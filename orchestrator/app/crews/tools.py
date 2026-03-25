"""Shared CrewAI tool functions wrapping infrastructure services."""

from __future__ import annotations

import asyncio
import json

from crewai.tools import tool

from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService


def _run_async(coro):
    """Run an async coroutine from synchronous CrewAI tool context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)


@tool("Brief Parser")
def brief_parser_tool(description: str) -> str:
    """Parse a free-text design brief and extract structured information.

    Returns a JSON string with detected garment type, keywords for fabric
    search, and normalized color palette extracted from the description.
    """
    description_lower = description.lower()

    garment_type = None
    garment_keywords = {
        "top": ["t-shirt", "tee", "blouse", "shirt", "top", "polo", "tank"],
        "bottom": ["pants", "trousers", "skirt", "shorts", "jeans"],
        "dress": ["dress", "gown", "jumpsuit", "romper"],
        "outerwear": ["jacket", "coat", "blazer", "hoodie", "parka", "vest"],
        "accessory": ["hat", "scarf", "bag", "belt", "gloves"],
    }
    for gtype, keywords in garment_keywords.items():
        if any(kw in description_lower for kw in keywords):
            garment_type = gtype
            break

    fabric_keywords = []
    fabric_terms = [
        "cotton", "silk", "polyester", "linen", "wool", "denim",
        "jersey", "chiffon", "satin", "velvet", "twill", "canvas",
        "fleece", "nylon", "cashmere", "organic", "recycled",
        "sustainable", "lightweight", "heavyweight",
    ]
    for term in fabric_terms:
        if term in description_lower:
            fabric_keywords.append(term)

    colors = []
    color_terms = [
        "black", "white", "navy", "cream", "grey", "gray", "red",
        "blue", "green", "pink", "beige", "khaki", "indigo",
        "burgundy", "olive", "coral", "ivory", "charcoal",
    ]
    for color in color_terms:
        if color in description_lower:
            colors.append(color)

    result = {
        "garment_type": garment_type,
        "fabric_keywords": fabric_keywords,
        "color_palette": colors,
        "original_description": description,
    }
    return json.dumps(result, indent=2)


@tool("Fabric Search")
def fabric_search_tool(query: str) -> str:
    """Search the fabric catalog for matching fabrics based on a text query.

    Uses semantic similarity search against the Supabase pgvector fabric
    catalog. Returns a JSON array of matching fabrics ranked by similarity.
    """
    rag = RAGService()
    results = _run_async(rag.search_fabrics(query, limit=5))
    return json.dumps(results, indent=2, default=str)


@tool("Text Embedding")
def embedding_tool(text: str) -> str:
    """Generate a text embedding vector for the given text.

    Returns the embedding as a JSON array of floats (1536 dimensions).
    Useful for computing similarity between fabric descriptions.
    """
    service = EmbeddingService()
    embedding = _run_async(service.embed_text(text))
    return json.dumps({"dimensions": len(embedding), "preview": embedding[:5]})
