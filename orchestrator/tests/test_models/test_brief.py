"""Tests for brief domain models."""

import pytest
from pydantic import ValidationError

from app.models.brief import DesignBrief, GarmentType


class TestGarmentType:
    def test_all_enum_values(self):
        assert GarmentType.TOP == "top"
        assert GarmentType.BOTTOM == "bottom"
        assert GarmentType.DRESS == "dress"
        assert GarmentType.OUTERWEAR == "outerwear"
        assert GarmentType.ACCESSORY == "accessory"

    def test_enum_count(self):
        assert len(GarmentType) == 5

    def test_enum_is_str(self):
        assert isinstance(GarmentType.TOP, str)


class TestDesignBrief:
    def test_valid_full_brief(self):
        brief = DesignBrief(
            description="A relaxed-fit linen shirt for summer",
            garment_type=GarmentType.TOP,
            target_season="SS26",
            style_references=["https://example.com/ref1"],
            fabric_preferences=["organic cotton", "linen"],
            color_palette=["#2C3E50", "navy"],
        )
        assert brief.description == "A relaxed-fit linen shirt for summer"
        assert brief.garment_type == GarmentType.TOP
        assert brief.target_season == "SS26"
        assert len(brief.style_references) == 1
        assert len(brief.fabric_preferences) == 2
        assert len(brief.color_palette) == 2

    def test_valid_minimal_brief(self):
        brief = DesignBrief(description="A simple t-shirt")
        assert brief.description == "A simple t-shirt"
        assert brief.garment_type is None
        assert brief.target_season is None
        assert brief.style_references == []
        assert brief.fabric_preferences == []
        assert brief.color_palette == []

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            DesignBrief()

    def test_empty_description_raises(self):
        with pytest.raises(ValidationError):
            DesignBrief(description="")

    def test_invalid_garment_type_raises(self):
        with pytest.raises(ValidationError):
            DesignBrief(description="test", garment_type="invalid")

    def test_serialization_roundtrip(self):
        brief = DesignBrief(
            description="Test brief",
            garment_type=GarmentType.DRESS,
            target_season="AW26",
        )
        data = brief.model_dump()
        restored = DesignBrief(**data)
        assert restored == brief
