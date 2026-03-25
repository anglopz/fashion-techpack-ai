"""Tests for BOM domain models."""

import pytest
from pydantic import ValidationError

from app.models.bom import BOMItem


class TestBOMItem:
    def test_valid_full_bom_item(self):
        item = BOMItem(
            category="fabric",
            description="Main body fabric",
            quantity="2.5",
            unit="meters",
            color="Navy",
            supplier="Albini Group",
        )
        assert item.category == "fabric"
        assert item.quantity == "2.5"
        assert item.unit == "meters"
        assert item.color == "Navy"
        assert item.supplier == "Albini Group"

    def test_valid_minimal_bom_item(self):
        item = BOMItem(
            category="trim",
            description="Main label",
            quantity="1",
            unit="pieces",
        )
        assert item.color is None
        assert item.supplier is None

    def test_missing_category_raises(self):
        with pytest.raises(ValidationError):
            BOMItem(description="test", quantity="1", unit="pieces")

    def test_empty_category_raises(self):
        with pytest.raises(ValidationError):
            BOMItem(category="", description="test", quantity="1", unit="pieces")

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            BOMItem(category="fabric", quantity="1", unit="meters")

    def test_missing_quantity_raises(self):
        with pytest.raises(ValidationError):
            BOMItem(category="fabric", description="test", unit="meters")

    def test_missing_unit_raises(self):
        with pytest.raises(ValidationError):
            BOMItem(category="fabric", description="test", quantity="1")

    def test_various_categories(self):
        categories = ["fabric", "trim", "hardware", "thread", "label"]
        for cat in categories:
            item = BOMItem(
                category=cat,
                description=f"{cat} item",
                quantity="1",
                unit="pieces",
            )
            assert item.category == cat
