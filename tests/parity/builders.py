"""Build engine objects from the ``input`` block of a parity fixture."""

from app.engine.conditions.seismic import SeismicCondition
from app.engine.conditions.wind import WindCondition
from app.engine.calculators.pole import PoleCalculator
from app.engine.geometry.pole_assembly import PoleAssembly
from app.engine.loads.base import OverdesignFactor
from app.engine.loads.pole import PoleObject
from app.engine.calculators.direct_object import DirectObjectCalculator
from app.engine.calculators.overhead_wire import OverheadWireCalculator
from app.engine.loads.direct_object import DirectObject
from app.engine.loads.overhead_wire import OverheadWire
from app.engine.calculators.section_check import EvaluatedPositionCalculator


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


def build_direct_object_calculator(case_input: dict, wind, seismic):
    """None when the case has no Direct Object, like the fixture generator."""
    if not case_input["direct_objects"]:
        return None
    return DirectObjectCalculator(
        [DirectObject(**item) for item in case_input["direct_objects"]],
        wind,
        seismic,
    )


def build_overhead_wire_calculator(case_input: dict, wind, seismic):
    """None when the case has no overhead wire, like the fixture generator."""
    if not case_input["overhead_wires"]:
        return None
    return OverheadWireCalculator(
        [OverheadWire(**item) for item in case_input["overhead_wires"]],
        wind,
        seismic,
    )


def build_section_check(case_input: dict, seismic_absent: bool = False):
    wind = build_wind(case_input)
    seismic = None if seismic_absent else build_seismic(case_input["seismic"])
    return EvaluatedPositionCalculator(
        build_pole_calculator(case_input, wind, seismic),
        build_direct_object_calculator(case_input, wind, seismic),
        build_overhead_wire_calculator(case_input, wind, seismic),
    )
