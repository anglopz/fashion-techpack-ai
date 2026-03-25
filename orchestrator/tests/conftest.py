"""Shared pytest fixtures for the orchestrator test suite."""
import pytest


@pytest.fixture
def sample_brief_text():
    """Sample design brief text for testing agents and services."""
    return "Relaxed-fit organic cotton t-shirt for SS26 in navy and cream colorway"
