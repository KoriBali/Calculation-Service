"""Engine deviation from python_calc: the seismic condition is optional."""

import pytest

from app.engine.calculators.direct_object import DirectObjectCalculator
from app.engine.calculators.pole import PoleCalculator
from app.engine.calculators.section_check import EvaluatedPositionCalculator
from app.engine.conditions.seismic import SeismicCondition
from app.engine.conditions.wind import WindCondition
from app.engine.geometry.pole_assembly import PoleAssembly
from app.engine.loads.direct_object import DirectObject
from app.engine.loads.pole import PoleObject

WIND = WindCondition(3, 8.0)
SEISMIC = SeismicCondition.ground(0.5)


def pole_calculator(seismic):
    pole = PoleObject("P", "Straight", 139.8, 139.8, 4.5, 4.5, "STK400", 8.0)
    return PoleCalculator(PoleAssembly([pole]), WIND, seismic)


def direct_object_calculator(seismic):
    lamp = DirectObject("L", "Omni", 0.3, 0, 10, 8.0, 1.0, 1, 0)
    return DirectObjectCalculator([lamp], WIND, seismic)


def test_without_seismic_every_seismic_result_is_none():
    result = EvaluatedPositionCalculator(
        pole_calculator(None), direct_object_calculator(None)
    ).calculate_at(0.0)

    assert result.total_seismic_load_n is None
    assert result.total_seismic_moment_nm is None
    assert result.total_fix_load_n > 0  # FixLoad does not depend on seismic
    for item in result.directional_results:
        assert item.seismic_strength is None
        assert item.resultant_seismic_load_n is None
        assert item.combined_seismic_moment_nm is None
        assert item.wind_strength.status in {"O.K", "N.G"}


def test_wind_result_does_not_change_when_seismic_is_removed():
    with_seismic = EvaluatedPositionCalculator(pole_calculator(SEISMIC)).calculate_at(0.0)
    without = EvaluatedPositionCalculator(pole_calculator(None)).calculate_at(0.0)
    for a, b in zip(with_seismic.directional_results, without.directional_results):
        assert a.wind_strength == b.wind_strength


def test_mixed_seismic_presence_is_rejected():
    with pytest.raises(ValueError, match="every calculator or to none"):
        EvaluatedPositionCalculator(
            pole_calculator(SEISMIC), direct_object_calculator(None)
        )


def test_utilization_exactly_one_is_not_ok():
    strength = EvaluatedPositionCalculator._strength_result(
        bending_moment_nm=8.0,
        section_modulus_cm3=2.0,
        allowable_stress_n_mm2=4.0,
    )
    assert strength.utilization_ratio == 1.0
    assert strength.status == "N.G"