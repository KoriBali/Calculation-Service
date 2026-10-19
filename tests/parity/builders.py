"""Build engine objects from the ``input`` block of a parity fixture."""

from app.engine.conditions.seismic import SeismicCondition
from app.engine.conditions.wind import WindCondition
from app.engine.calculators.pole import PoleCalculator
from app.engine.geometry.pole_assembly import PoleAssembly
from app.engine.loads.base import OverdesignFactor
from app.engine.loads.pole import PoleObject

def build_wind(case_input: dict) -> WindCondition:
    return WindCondition(**case_input["wind"])


def build_seismic(seismic_input: dict | None) -> SeismicCondition | None:
    if seismic_input is None:
        return None
    if seismic_input["position"] == "Ground":
        return SeismicCondition.ground(seismic_input["k_value"])
    return SeismicCondition.rooftop(seismic_input["seismic_class"])


def build_pole_calculator(case_input: dict, wind, seismic) -> PoleCalculator:
    return PoleCalculator(
        assembly=PoleAssembly(
            [PoleObject(**pole) for pole in case_input["poles"]],
            base_elevation_m=case_input["base_elevation_m"],
        ),
        wind_condition=wind,
        seismic_condition=seismic,
        overdesign_factor=OverdesignFactor(case_input["overdesign_factor"]),
    )
