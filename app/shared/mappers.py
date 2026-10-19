"""Engine results -> JSON-ready dicts. Full precision, no rounding."""

from dataclasses import asdict

from app.engine.conditions.wind import WindCondition


def map_result(result) -> dict | None:
    """Any engine result dataclass -> snake_case dict (None stays None)."""
    return None if result is None else asdict(result)


def map_wind_condition(wind: WindCondition) -> dict:
    common = wind.common_parameters
    return {
        "design_standard": wind.design_standard,
        "structure_height_m": wind.structure_height_m,
        "atmospheric_category": wind.atmospheric_category,
        "basic_wind_speed_m_s": wind.basic_wind_speed_m_s,
        # Keys follow std_act_common() in app/engine/conditions/wind.py.
        "common_parameters": None if common is None else {
            "hstr": common["Hstr"],
            "zb": common["zb"],
            "zg": common["zg"],
            "alpha": common["alpha"],
            "gf": common["Gf"],
            "er": common["Er"],
            "ds_air": common["Ds_air"],
            "adc_symbol": common["ADC_symbol"],
        },
    }
