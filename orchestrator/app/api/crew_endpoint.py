"""FastAPI endpoint for running the CrewAI tech pack prototype."""

from __future__ import annotations

import json
import traceback
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.crews.techpack_crew import create_techpack_crew
from app.models import DesignBrief, TechPack

router = APIRouter(tags=["crew"])


@router.post("/crew/techpacks", status_code=202)
async def create_techpack_crew_run(brief: DesignBrief) -> dict:
    """Run the CrewAI prototype pipeline against a design brief.

    Returns 202 with the tech pack result (or error details).
    """
    try:
        crew = create_techpack_crew()
        result = crew.kickoff(inputs={"brief": brief.description})

        # Attempt to parse and validate the crew output as a TechPack
        raw_output = str(result)
        try:
            parsed = json.loads(raw_output)
            tech_pack = TechPack.model_validate(parsed)
            return {
                "id": tech_pack.id,
                "status": "completed",
                "engine": "crewai",
                "tech_pack": tech_pack.model_dump(),
            }
        except (json.JSONDecodeError, Exception):
            # Crew produced output but it didn't validate as TechPack
            # Return raw output with metadata for debugging
            return {
                "id": f"tp_{uuid.uuid4().hex[:8]}",
                "status": "completed",
                "engine": "crewai",
                "raw_output": raw_output,
                "validation_error": "Output did not validate against TechPack schema",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Crew execution failed",
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
