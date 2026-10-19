"""Engine results -> JSON-ready dicts. Full precision, no rounding."""

from dataclasses import asdict

from pydantic.alias_generators import to_camel

from app.engine.conditions.wind import WindCondition


def camelize(value):
    """Recursively convert snake_case dict keys to camelCase; tuples -> lists."""
    if isinstance(value, dict):
        return {to_camel(key): camelize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [camelize(item) for item in value]
    return value


def map_result(result) -> dict | None:
    """Any engine result dataclass -> camelCase dict (None stays None)."""
    return None if result is None else camelize(asdict(result))


def map_wind_condition(wind: WindCondition) -> dict:
    common = wind.common_parameters
    return {
        "designStandard": wind.design_standard,
        "structureHeightM": wind.structure_height_m,
        "atmosphericCategory": wind.atmospheric_category,
        "basicWindSpeedMS": wind.basic_wind_speed_m_s,
        # Keys follow std_act_common() in app/engine/conditions/wind.py.
        "commonParameters": None if common is None else {
            "hstr": common["Hstr"],
            "zb": common["zb"],
            "zg": common["zg"],
            "alpha": common["alpha"],
            "gf": common["Gf"],
            "er": common["Er"],
            "dsAir": common["Ds_air"],
            "adcSymbol": common["ADC_symbol"],
        },
    }