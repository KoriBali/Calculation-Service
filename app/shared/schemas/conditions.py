"""Wind and seismic input. The classifier field decides which fields exist."""

from typing import Annotated, Literal

from pydantic import Field, PositiveFloat

from app.shared.schemas.base import ApiModel


class WindAtmosphericInput(ApiModel):
    """Design standard 1 or 6: atmospheric category and wind speed required."""

    design_standard: Literal[1, 6]
    structure_height_m: PositiveFloat
    atmospheric_category: Literal[1, 2, 3, 4]
    basic_wind_speed_m_s: PositiveFloat


class WindFixedInput(ApiModel):
    """Design standard 2-5: wind pressure is a constant inside the engine."""

    design_standard: Literal[2, 3, 4, 5]
    structure_height_m: PositiveFloat


WindInput = Annotated[
    WindAtmosphericInput | WindFixedInput,
    Field(discriminator="design_standard"),
]


class SeismicGroundInput(ApiModel):
    position: Literal["Ground"]
    k_value: PositiveFloat


class SeismicRooftopInput(ApiModel):
    position: Literal["Rooftop"]
    seismic_class: Literal["A", "B", "S"]


SeismicInput = Annotated[
    SeismicGroundInput | SeismicRooftopInput,
    Field(discriminator="position"),
]