"""Tests for fabric domain models."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.fabric import FabricSpec

SEED_DIR = Path(__file__).resolve().parents[3] / "seed"


class TestFabricSpec:
    def test_valid_full_fabric(self):
        f = FabricSpec(
            name="Premium Organic Cotton Jersey",
            composition="100% Organic Cotton",
            weight_gsm=180.0,
            width_cm=150.0,
            color="White",
            supplier="Albini Group",
            price_per_meter=12.50,
            care_instructions=["Machine wash 30°C", "Tumble dry low"],
            similarity_score=0.92,
        )
        assert f.name == "Premium Organic Cotton Jersey"
        assert f.weight_gsm == 180.0
        assert f.supplier == "Albini Group"
        assert f.similarity_score == 0.92

    def test_valid_minimal_fabric(self):
        f = FabricSpec(
            name="Cotton",
            composition="100% Cotton",
            weight_gsm=150.0,
            width_cm=150.0,
            color="White",
        )
        assert f.supplier is None
        assert f.price_per_meter is None
        assert f.care_instructions == []
        assert f.similarity_score == 0.0

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            FabricSpec(
                composition="100% Cotton",
                weight_gsm=150.0,
                width_cm=150.0,
                color="White",
            )

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            FabricSpec(
                name="",
                composition="100% Cotton",
                weight_gsm=150.0,
                width_cm=150.0,
                color="White",
            )

    def test_zero_weight_raises(self):
        with pytest.raises(ValidationError):
            FabricSpec(
                name="Cotton",
                composition="100% Cotton",
                weight_gsm=0,
                width_cm=150.0,
                color="White",
            )

    def test_negative_weight_raises(self):
        with pytest.raises(ValidationError):
            FabricSpec(
                name="Cotton",
                composition="100% Cotton",
                weight_gsm=-10.0,
                width_cm=150.0,
                color="White",
            )

    def test_zero_width_raises(self):
        with pytest.raises(ValidationError):
            FabricSpec(
                name="Cotton",
                composition="100% Cotton",
                weight_gsm=150.0,
                width_cm=0,
                color="White",
            )

    def test_missing_composition_raises(self):
        with pytest.raises(ValidationError):
            FabricSpec(
                name="Cotton",
                weight_gsm=150.0,
                width_cm=150.0,
                color="White",
            )

    def test_missing_color_raises(self):
        with pytest.raises(ValidationError):
            FabricSpec(
                name="Cotton",
                composition="100% Cotton",
                weight_gsm=150.0,
                width_cm=150.0,
            )


class TestSeedFabrics:
    def test_seed_file_loads(self):
        fabrics_path = SEED_DIR / "fabrics.json"
        assert fabrics_path.exists(), f"Seed file not found: {fabrics_path}"
        with open(fabrics_path) as f:
            data = json.load(f)
        assert isinstance(data, list)

    def test_seed_has_50_plus_entries(self):
        with open(SEED_DIR / "fabrics.json") as f:
            data = json.load(f)
        assert len(data) >= 50, f"Expected 50+ fabrics, got {len(data)}"

    def test_seed_entries_validate(self):
        with open(SEED_DIR / "fabrics.json") as f:
            data = json.load(f)
        for i, entry in enumerate(data):
            try:
                FabricSpec(**entry)
            except ValidationError as e:
                pytest.fail(f"Fabric entry {i} ({entry.get('name')}) failed validation: {e}")

    def test_seed_has_diverse_fabrics(self):
        with open(SEED_DIR / "fabrics.json") as f:
            data = json.load(f)
        names = [d["name"].lower() for d in data]
        all_names = " ".join(names)
        expected_types = ["cotton", "silk", "polyester", "linen", "wool", "denim"]
        for fabric_type in expected_types:
            assert fabric_type in all_names, f"Missing fabric type: {fabric_type}"

    def test_seed_has_realistic_weights(self):
        with open(SEED_DIR / "fabrics.json") as f:
            data = json.load(f)
        for entry in data:
            gsm = entry["weight_gsm"]
            assert 20 <= gsm <= 500, f"{entry['name']} has unrealistic GSM: {gsm}"
