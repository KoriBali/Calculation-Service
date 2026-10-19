from app.engine.conditions.wind import WindCondition
from app.section_check.schemas import SectionCheckRequest
from app.shared.mappers import map_result, map_wind_condition

SCHEMA_VERSION = "1.0"


def map_section_check(
    request: SectionCheckRequest,
    wind: WindCondition,
    has_seismic: bool,
    positions: list[tuple],
) -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "checks": ["wind", "seismic"] if has_seismic else ["wind"],
        "designCondition": {
            "wind": map_wind_condition(wind),
            "seismic": (
                None
                if request.seismic is None
                else request.seismic.model_dump(by_alias=True)
            ),
            "overdesignFactor": request.overdesign_factor,
            "baseElevationM": request.base_elevation_m,
        },
        "evaluatedPositions": [
            {
                "evaluatedPositionM": position,
                "pole": map_result(pole),
                "directObject": map_result(direct_object),
                "sectionCheck": map_result(section),
            }
            for position, pole, direct_object, section in positions
        ],
    }
