"""FastAPI endpoints for LangGraph-powered tech pack generation."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.graphs.techpack_graph import build_techpack_graph
from app.models import DesignBrief, TechPackState

router = APIRouter(tags=["techpacks"])

# In-memory job store
_jobs: dict[str, dict[str, Any]] = {}


# --- Request / Response schemas ---


class CreateTechPackRequest(BaseModel):
    """Payload accepted by POST /techpacks."""

    description: str = Field(..., min_length=1)
    garment_type: str | None = None
    target_season: str | None = None
    fabric_preferences: list[str] = []
    color_palette: list[str] = []
    style_references: list[str] = []
    engine: str = "langgraph"


class CreateTechPackResponse(BaseModel):
    """Payload returned by POST /techpacks."""

    id: str
    status: str
    engine: str
    ws_url: str


# --- Background task ---


async def _run_graph(job_id: str, brief: DesignBrief) -> None:
    """Execute the LangGraph workflow in the background, streaming agent progress."""
    try:
        graph = build_techpack_graph()
        initial_state: TechPackState = {
            "brief": brief,
            "garment_type": None,
            "measurements": None,
            "fabrics": [],
            "bom": [],
            "construction": [],
            "tech_pack": None,
            "current_agent": "brief_analyzer",
            "agent_messages": [],
            "errors": [],
            "retry_count": 0,
        }
        final_state = None
        async for state in graph.astream(
            initial_state,
            config={"configurable": {"thread_id": job_id}},
            stream_mode="values",
        ):
            # Each event is the full state after a node completes
            final_state = state
            messages = state.get("agent_messages", [])
            if messages:
                _jobs[job_id]["agent_messages"] = messages
            _jobs[job_id]["current_agent"] = state.get("current_agent", "")

        _jobs[job_id]["status"] = "completed"
        if final_state:
            _jobs[job_id]["result"] = _serialize_result(final_state)
    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(exc)


def _serialize_result(state: dict[str, Any]) -> dict[str, Any]:
    """Extract serializable result data from the final graph state."""
    result: dict[str, Any] = {}

    # Serialize Pydantic models and plain dicts
    for key in ("tech_pack", "measurements"):
        val = state.get(key)
        if val is not None:
            result[key] = val.model_dump() if hasattr(val, "model_dump") else val

    # Serialize lists of Pydantic models
    for key in ("fabrics", "bom", "construction"):
        items = state.get(key, [])
        result[key] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in items
        ]

    if state.get("garment_type"):
        gt = state["garment_type"]
        result["garment_type"] = gt.value if hasattr(gt, "value") else str(gt)

    return result


# --- Endpoints ---


@router.post("/techpacks", status_code=202, response_model=CreateTechPackResponse)
async def create_techpack(request: CreateTechPackRequest) -> CreateTechPackResponse:
    """Start a new tech pack generation job."""
    job_id = f"tp_{uuid.uuid4().hex[:8]}"
    brief = DesignBrief(
        description=request.description,
        garment_type=request.garment_type,
        target_season=request.target_season,
        fabric_preferences=request.fabric_preferences,
        color_palette=request.color_palette,
        style_references=request.style_references,
    )

    _jobs[job_id] = {
        "status": "processing",
        "engine": request.engine,
        "agent_messages": [],
    }

    asyncio.create_task(_run_graph(job_id, brief))

    return CreateTechPackResponse(
        id=job_id,
        status="processing",
        engine=request.engine,
        ws_url=f"/api/v1/techpacks/{job_id}/stream",
    )


@router.get("/techpacks/{techpack_id}")
async def get_techpack(techpack_id: str) -> dict[str, Any]:
    """Return the current status and result of a tech pack job."""
    if techpack_id not in _jobs:
        raise HTTPException(status_code=404, detail="Tech pack not found")
    return {"id": techpack_id, **_jobs[techpack_id]}


@router.websocket("/techpacks/{techpack_id}/stream")
async def stream_techpack(websocket: WebSocket, techpack_id: str) -> None:
    """Stream agent messages over WebSocket until the job completes."""
    await websocket.accept()

    if techpack_id not in _jobs:
        await websocket.send_json({"error": "Tech pack not found"})
        await websocket.close()
        return

    sent_count = 0
    try:
        while True:
            job = _jobs[techpack_id]
            messages = job.get("agent_messages", [])

            # Send any new messages
            while sent_count < len(messages):
                await websocket.send_json(messages[sent_count])
                sent_count += 1

            if job["status"] in ("completed", "failed"):
                await websocket.send_json(
                    {"event": "done", "status": job["status"]}
                )
                break

            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
