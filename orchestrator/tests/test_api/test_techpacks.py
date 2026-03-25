"""Tests for the LangGraph tech pack API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.techpacks import _jobs
from app.main import create_app


@pytest.fixture()
def client(mocker) -> TestClient:
    """Create a test client with redis mocked out."""
    mocker.patch("app.main.redis_service.connect")
    mocker.patch("app.main.redis_service.close")
    app = create_app()
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_jobs():
    """Reset the in-memory job store between tests."""
    _jobs.clear()
    yield
    _jobs.clear()


VALID_PAYLOAD = {
    "description": "A minimalist linen summer dress",
    "garment_type": "dress",
    "target_season": "SS26",
    "fabric_preferences": ["linen"],
    "color_palette": ["white", "beige"],
    "style_references": [],
}


class TestPostTechpacks:
    """POST /api/v1/techpacks."""

    def test_accepts_valid_brief(self, client: TestClient, mocker) -> None:
        mocker.patch("app.api.techpacks.asyncio.create_task")
        resp = client.post("/api/v1/techpacks", json=VALID_PAYLOAD)
        assert resp.status_code == 202
        body = resp.json()
        assert "id" in body
        assert body["status"] == "processing"
        assert body["engine"] == "langgraph"
        assert "ws_url" in body

    def test_rejects_empty_description(self, client: TestClient, mocker) -> None:
        mocker.patch("app.api.techpacks.asyncio.create_task")
        payload = {**VALID_PAYLOAD, "description": ""}
        resp = client.post("/api/v1/techpacks", json=payload)
        assert resp.status_code == 422

    def test_default_engine_is_langgraph(self, client: TestClient, mocker) -> None:
        mocker.patch("app.api.techpacks.asyncio.create_task")
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "engine"}
        resp = client.post("/api/v1/techpacks", json=payload)
        assert resp.status_code == 202
        assert resp.json()["engine"] == "langgraph"


class TestGetTechpack:
    """GET /api/v1/techpacks/{techpack_id}."""

    def test_returns_404_for_unknown_id(self, client: TestClient) -> None:
        resp = client.get("/api/v1/techpacks/nonexistent")
        assert resp.status_code == 404

    def test_returns_processing_status(self, client: TestClient, mocker) -> None:
        mocker.patch("app.api.techpacks.asyncio.create_task")
        post_resp = client.post("/api/v1/techpacks", json=VALID_PAYLOAD)
        job_id = post_resp.json()["id"]
        get_resp = client.get(f"/api/v1/techpacks/{job_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "processing"
