"""Validated request schemas -> engine objects. No formulas here."""

from app.engine.conditions.seismic import SeismicCondition
from app.engine.conditions.wind import WindCondition
from app.engine.loads.direct_object import DirectObject
from app.engine.loads.pole import PoleObject
from app.shared.schemas.conditions import (
    SeismicGroundInput,
    SeismicInput,
    WindAtmosphericInput,
    WindInput,
)
from app.shared.schemas.direct_object import DirectObjectInput, OmniObjectInput
from app.shared.schemas.pole import PoleSegmentInput, StraightPoleInput


def to_wind_condition(wind: WindInput) -> WindCondition:
    if isinstance(wind, WindAtmosphericInput):
        return WindCondition(
            design_standard=wind.design_standard,
            structure_height_m=wind.structure_height_m,
            atmospheric_category=wind.atmospheric_category,
            basic_wind_speed_m_s=wind.basic_wind_speed_m_s,
        )
    return WindCondition(
        design_standard=wind.design_standard,
        structure_height_m=wind.structure_height_m,
    )


def to_seismic_condition(seismic: SeismicInput | None) -> SeismicCondition | None:
    if seismic is None:
        return None
    if isinstance(seismic, SeismicGroundInput):
        return SeismicCondition.ground(seismic.k_value)
    return SeismicCondition.rooftop(seismic.seismic_class)


def to_pole_object(pole: PoleSegmentInput) -> PoleObject:
    if isinstance(pole, StraightPoleInput):
        # The engine reads only the lower values of a straight segment.
        diameter_lower = diameter_upper = pole.diameter_mm
        thickness_lower = thickness_upper = pole.thickness_mm
    else:
        diameter_lower = pole.diameter_lower_mm
        diameter_upper = pole.diameter_upper_mm
        thickness_lower = pole.thickness_lower_mm
        thickness_upper = pole.thickness_upper_mm
    return PoleObject(
        name=pole.name,
        pole_type=pole.pole_type,
        diameter_lower_mm=diameter_lower,
        diameter_upper_mm=diameter_upper,
        thickness_lower_mm=thickness_lower,
        thickness_upper_mm=thickness_upper,
        material=pole.material,
        top_elevation_m=pole.top_elevation_m,
    )


def to_direct_object(item: DirectObjectInput) -> DirectObject:
    if isinstance(item, OmniObjectInput):
        # Omni uses the front area for every direction; side area and angle
        # do not change any load. 0 keeps the reported angle factors neutral.
        side_area, fixed_angle = 0.0, 0.0
    else:
        side_area, fixed_angle = item.side_area_m2, item.fixed_angle_deg
    return DirectObject(
        name=item.name,
        object_type=item.object_type,
        front_area_m2=item.front_area_m2,
        side_area_m2=side_area,
        mass_per_unit_kg=item.mass_per_unit_kg,
        elevation_m=item.elevation_m,
        base_wind_coefficient=item.base_wind_coefficient,
        quantity=item.quantity,
        fixed_angle_deg=fixed_angle,
    )