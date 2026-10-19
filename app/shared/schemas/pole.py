"""Pole segment input. ``poleType`` decides which dimensions exist."""

from typing import Annotated, Literal

from pydantic import Field, PositiveFloat, StringConstraints, field_validator

from app.engine.materials import MATERIALS
from app.shared.schemas.base import ApiModel

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class _PoleSegmentBase(ApiModel):
    name: Name
    material: Name
    top_elevation_m: PositiveFloat

    @field_validator("material")
    @classmethod
    def _known_material(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in MATERIALS:
            raise ValueError(f"unknown material, expected one of {sorted(MATERIALS)}")
        return normalized


class StraightPoleInput(_PoleSegmentBase):
    """Straight segment: one diameter and one thickness."""

    pole_type: Literal["Straight"]
    diameter_mm: PositiveFloat
    thickness_mm: PositiveFloat


class TaperPoleInput(_PoleSegmentBase):
    pole_type: Literal["Taper"]
    diameter_lower_mm: PositiveFloat
    diameter_upper_mm: PositiveFloat
    thickness_lower_mm: PositiveFloat
    thickness_upper_mm: PositiveFloat


PoleSegmentInput = Annotated[
    StraightPoleInput | TaperPoleInput,
    Field(discriminator="pole_type"),
]