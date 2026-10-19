"""Direct Object input. ``object_type`` decides which fields exist."""

from typing import Annotated, Literal

from pydantic import Field, NonNegativeFloat, PositiveFloat, PositiveInt

from app.shared.schemas.base import ApiModel
from app.shared.schemas.pole import Name


class _DirectObjectBase(ApiModel):
    name: Name
    front_area_m2: PositiveFloat
    mass_per_unit_kg: NonNegativeFloat
    elevation_m: NonNegativeFloat
    base_wind_coefficient: PositiveFloat
    quantity: PositiveInt


class OmniObjectInput(_DirectObjectBase):
    """Same projected area from every direction: no side area, no angle."""

    object_type: Literal["Omni"]


class DirectionalObjectInput(_DirectObjectBase):
    object_type: Literal["Directional"]
    side_area_m2: NonNegativeFloat
    fixed_angle_deg: float


DirectObjectInput = Annotated[
    OmniObjectInput | DirectionalObjectInput,
    Field(discriminator="object_type"),
]