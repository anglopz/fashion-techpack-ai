"""Tests for the CrewAI API endpoint."""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    """Create a test client with mocked lifespan."""
    app = create_app()
    return TestClient(app)


class TestCrewEndpoint:
    """Tests for POST /api/v1/crew/techpacks."""

    @patch("app.api.crew_endpoint.create_techpack_crew")
    def test_returns_202_on_success(self, mock_create_crew, client):
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = json.dumps({
            "id": "tp_test123",
            "brief": {
                "description": "Test brief",
            },
            "measurements": {
                "garment_type": "top",
                "size_range": "XS-XL",
                "key_measurements": {"chest": {"S": 88}},
                "fit_type": "relaxed",
            },
            "primary_fabric": {
                "name": "Organic Cotton",
                "composition": "100% Cotton",
                "weight_gsm": 180,
                "width_cm": 150,
                "color": "White",
            },
            "bom": [
                {
                    "category": "fabric",
                    "description": "Main body fabric",
                    "quantity": "2.5",
                    "unit": "meters",
                }
            ],
            "construction": [
                {
                    "step": 1,
                    "description": "Cut pattern pieces",
                }
            ],
            "status": "draft",
            "created_at": "2026-03-25T00:00:00Z",
            "version": 1,
        })
        mock_create_crew.return_value = mock_crew

        response = client.post(
            "/api/v1/crew/techpacks",
            json={
                "description": "Relaxed-fit organic cotton t-shirt for SS26",
                "garment_type": "top",
                "fabric_preferences": ["organic cotton"],
                "color_palette": ["navy", "cream"],
            },
        )
        assert response.status_code == 202
        data = response.json()
        assert data["engine"] == "crewai"
        assert data["status"] == "completed"

    @patch("app.api.crew_endpoint.create_techpack_crew")
    def test_handles_invalid_crew_output(self, mock_create_crew, client):
        """When crew returns non-JSON, endpoint should still return 202."""
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Some non-JSON crew output"
        mock_create_crew.return_value = mock_crew

        response = client.post(
            "/api/v1/crew/techpacks",
            json={"description": "A simple t-shirt"},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["engine"] == "crewai"
        assert "raw_output" in data

    @patch("app.api.crew_endpoint.create_techpack_crew")
    def test_returns_500_on_crew_failure(self, mock_create_crew, client):
        mock_crew = MagicMock()
        mock_crew.kickoff.side_effect = RuntimeError("LLM call failed")
        mock_create_crew.return_value = mock_crew

        response = client.post(
            "/api/v1/crew/techpacks",
            json={"description": "A test brief"},
        )
        assert response.status_code == 500
        data = response.json()
        assert "LLM call failed" in data["detail"]["message"]

    def test_rejects_empty_description(self, client):
        response = client.post(
            "/api/v1/crew/techpacks",
            json={"description": ""},
        )
        assert response.status_code == 422
