"""Tests for techpack domain models."""

import pytest
from pydantic import ValidationError

from app.models.bom import BOMItem
from app.models.brief import DesignBrief, GarmentType
from app.models.fabric import FabricSpec
from app.models.measurements import Measurements
from app.models.techpack import ConstructionDetail, TechPack


@pytest.fixture
def sample_brief():
    return DesignBrief(
        description="A relaxed-fit linen shirt",
        garment_type=GarmentType.TOP,
    )


@pytest.fixture
def sample_measurements():
    return Measurements(
        garment_type=GarmentType.TOP,
        size_range="XS-XL",
        key_measurements={"chest": {"XS": 84.0, "S": 88.0}},
        fit_type="relaxed",
    )


@pytest.fixture
def sample_fabric():
    return FabricSpec(
        name="French Linen",
        composition="100% Linen",
        weight_gsm=190.0,
        width_cm=140.0,
        color="Natural",
    )


@pytest.fixture
def sample_bom():
    return [
        BOMItem(category="fabric", description="Main body", quantity="2.5", unit="meters"),
        BOMItem(category="thread", description="Matching thread", quantity="1", unit="rolls"),
    ]


@pytest.fixture
def sample_construction():
    return [
        ConstructionDetail(step=1, description="Cut pattern pieces", stitch_type=None),
        ConstructionDetail(step=2, description="Sew shoulder seams", stitch_type="lockstitch", seam_allowance="1cm"),
    ]


class TestConstructionDetail:
    def test_valid_full(self):
        c = ConstructionDetail(
            step=1,
            description="Sew side seams",
            stitch_type="lockstitch",
            seam_allowance="1cm",
        )
        assert c.step == 1
        assert c.stitch_type == "lockstitch"

    def test_valid_minimal(self):
        c = ConstructionDetail(step=1, description="Cut pieces")
        assert c.stitch_type is None
        assert c.seam_allowance is None

    def test_zero_step_raises(self):
        with pytest.raises(ValidationError):
            ConstructionDetail(step=0, description="test")

    def test_negative_step_raises(self):
        with pytest.raises(ValidationError):
            ConstructionDetail(step=-1, description="test")

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            ConstructionDetail(step=1)

    def test_empty_description_raises(self):
        with pytest.raises(ValidationError):
            ConstructionDetail(step=1, description="")


class TestTechPack:
    def test_valid_techpack(
        self, sample_brief, sample_measurements, sample_fabric, sample_bom, sample_construction
    ):
        tp = TechPack(
            id="abc-123",
            brief=sample_brief,
            measurements=sample_measurements,
            primary_fabric=sample_fabric,
            bom=sample_bom,
            construction=sample_construction,
            created_at="2026-03-25T12:00:00Z",
        )
        assert tp.id == "abc-123"
        assert tp.status == "draft"
        assert tp.version == 1
        assert len(tp.bom) == 2
        assert len(tp.construction) == 2
        assert tp.secondary_fabrics == []
        assert tp.colorways == []

    def test_techpack_with_optionals(
        self, sample_brief, sample_measurements, sample_fabric, sample_bom, sample_construction
    ):
        tp = TechPack(
            id="def-456",
            brief=sample_brief,
            measurements=sample_measurements,
            primary_fabric=sample_fabric,
            secondary_fabrics=[sample_fabric],
            bom=sample_bom,
            construction=sample_construction,
            colorways=[{"name": "Midnight", "hex": "#2C3E50"}],
            status="review",
            created_at="2026-03-25T12:00:00Z",
            version=2,
        )
        assert len(tp.secondary_fabrics) == 1
        assert len(tp.colorways) == 1
        assert tp.status == "review"
        assert tp.version == 2

    def test_missing_id_raises(
        self, sample_brief, sample_measurements, sample_fabric, sample_bom, sample_construction
    ):
        with pytest.raises(ValidationError):
            TechPack(
                brief=sample_brief,
                measurements=sample_measurements,
                primary_fabric=sample_fabric,
                bom=sample_bom,
                construction=sample_construction,
                created_at="2026-03-25T12:00:00Z",
            )

    def test_missing_brief_raises(
        self, sample_measurements, sample_fabric, sample_bom, sample_construction
    ):
        with pytest.raises(ValidationError):
            TechPack(
                id="abc",
                measurements=sample_measurements,
                primary_fabric=sample_fabric,
                bom=sample_bom,
                construction=sample_construction,
                created_at="2026-03-25T12:00:00Z",
            )

    def test_serialization_roundtrip(
        self, sample_brief, sample_measurements, sample_fabric, sample_bom, sample_construction
    ):
        tp = TechPack(
            id="test-123",
            brief=sample_brief,
            measurements=sample_measurements,
            primary_fabric=sample_fabric,
            bom=sample_bom,
            construction=sample_construction,
            created_at="2026-03-25T12:00:00Z",
        )
        data = tp.model_dump()
        restored = TechPack(**data)
        assert restored == tp
