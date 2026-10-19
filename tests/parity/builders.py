"""Build engine objects from the ``input`` block of a parity fixture."""

from app.engine.conditions.seismic import SeismicCondition
from app.engine.conditions.wind import WindCondition


def build_wind(case_input: dict) -> WindCondition:
    return WindCondition(**case_input["wind"])


def build_seismic(seismic_input: dict | None) -> SeismicCondition | None:
    if seismic_input is None:
        return None
    if seismic_input["position"] == "Ground":
        return SeismicCondition.ground(seismic_input["k_value"])
    return SeismicCondition.rooftop(seismic_input["seismic_class"])
