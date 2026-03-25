"""Tests for measurements domain models."""

import pytest
from pydantic import ValidationError

from app.models.brief import GarmentType
from app.models.measurements import Measurements


class TestMeasurements:
    def test_valid_measurements(self):
        m = Measurements(
            garment_type=GarmentType.TOP,
            size_range="XS-XL",
            key_measurements={"chest": {"XS": 84.0, "S": 88.0, "M": 92.0}},
            fit_type="relaxed",
            notes=["Measured flat"],
        )
        assert m.garment_type == GarmentType.TOP
        assert m.size_range == "XS-XL"
        assert m.key_measurements["chest"]["S"] == 88.0
        assert m.fit_type == "relaxed"
        assert len(m.notes) == 1

    def test_minimal_measurements(self):
        m = Measurements(
            garment_type=GarmentType.BOTTOM,
            size_range="S-L",
            key_measurements={"waist": {"S": 72.0}},
            fit_type="slim",
        )
        assert m.notes == []

    def test_missing_garment_type_raises(self):
        with pytest.raises(ValidationError):
            Measurements(
                size_range="XS-XL",
                key_measurements={"chest": {"S": 88.0}},
                fit_type="relaxed",
            )

    def test_missing_size_range_raises(self):
        with pytest.raises(ValidationError):
            Measurements(
                garment_type=GarmentType.TOP,
                key_measurements={"chest": {"S": 88.0}},
                fit_type="relaxed",
            )

    def test_empty_size_range_raises(self):
        with pytest.raises(ValidationError):
            Measurements(
                garment_type=GarmentType.TOP,
                size_range="",
                key_measurements={"chest": {"S": 88.0}},
                fit_type="relaxed",
            )

    def test_missing_fit_type_raises(self):
        with pytest.raises(ValidationError):
            Measurements(
                garment_type=GarmentType.TOP,
                size_range="XS-XL",
                key_measurements={"chest": {"S": 88.0}},
            )

    def test_empty_fit_type_raises(self):
        with pytest.raises(ValidationError):
            Measurements(
                garment_type=GarmentType.TOP,
                size_range="XS-XL",
                key_measurements={"chest": {"S": 88.0}},
                fit_type="",
            )

    def test_missing_key_measurements_raises(self):
        with pytest.raises(ValidationError):
            Measurements(
                garment_type=GarmentType.TOP,
                size_range="XS-XL",
                fit_type="relaxed",
            )
