"""Tests for CrewAI shared tools."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.crews.tools import brief_parser_tool, embedding_tool, fabric_search_tool


class TestBriefParserTool:
    """Tests for the brief_parser_tool."""

    def test_detects_top_garment_type(self):
        result = json.loads(
            brief_parser_tool.run("Relaxed-fit organic cotton t-shirt for SS26")
        )
        assert result["garment_type"] == "top"

    def test_detects_bottom_garment_type(self):
        result = json.loads(
            brief_parser_tool.run("Slim-fit denim jeans in dark indigo")
        )
        assert result["garment_type"] == "bottom"

    def test_detects_dress_garment_type(self):
        result = json.loads(
            brief_parser_tool.run("Flowing silk dress for evening wear")
        )
        assert result["garment_type"] == "dress"

    def test_detects_outerwear_garment_type(self):
        result = json.loads(
            brief_parser_tool.run("Wool blazer with structured shoulders")
        )
        assert result["garment_type"] == "outerwear"

    def test_extracts_fabric_keywords(self):
        result = json.loads(
            brief_parser_tool.run("Organic cotton jersey t-shirt, lightweight")
        )
        assert "cotton" in result["fabric_keywords"]
        assert "organic" in result["fabric_keywords"]
        assert "jersey" in result["fabric_keywords"]
        assert "lightweight" in result["fabric_keywords"]

    def test_extracts_colors(self):
        result = json.loads(
            brief_parser_tool.run("Navy and cream colorway t-shirt")
        )
        assert "navy" in result["color_palette"]
        assert "cream" in result["color_palette"]

    def test_preserves_original_description(self):
        desc = "A simple white cotton shirt"
        result = json.loads(brief_parser_tool.run(desc))
        assert result["original_description"] == desc

    def test_unknown_garment_type_returns_none(self):
        result = json.loads(brief_parser_tool.run("Something very abstract"))
        assert result["garment_type"] is None


class TestFabricSearchTool:
    """Tests for the fabric_search_tool (mocked)."""

    @patch("app.crews.tools.RAGService")
    def test_returns_search_results(self, mock_rag_cls):
        mock_instance = mock_rag_cls.return_value
        mock_instance.search_fabrics = AsyncMock(
            return_value=[
                {"name": "Organic Cotton Jersey", "similarity": 0.92},
                {"name": "Cotton Poplin", "similarity": 0.87},
            ]
        )
        result = json.loads(fabric_search_tool.run("lightweight cotton"))
        assert len(result) == 2
        assert result[0]["name"] == "Organic Cotton Jersey"

    @patch("app.crews.tools.RAGService")
    def test_returns_empty_on_no_results(self, mock_rag_cls):
        mock_instance = mock_rag_cls.return_value
        mock_instance.search_fabrics = AsyncMock(return_value=[])
        result = json.loads(fabric_search_tool.run("nonexistent fabric"))
        assert result == []


class TestEmbeddingTool:
    """Tests for the embedding_tool (mocked)."""

    @patch("app.crews.tools.EmbeddingService")
    def test_returns_embedding_info(self, mock_emb_cls):
        mock_instance = mock_emb_cls.return_value
        fake_embedding = [0.1] * 1536
        mock_instance.embed_text = AsyncMock(return_value=fake_embedding)
        result = json.loads(embedding_tool.run("test text"))
        assert result["dimensions"] == 1536
        assert len(result["preview"]) == 5
