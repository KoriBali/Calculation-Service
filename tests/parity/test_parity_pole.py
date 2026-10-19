"""Parity: engine pole calculator == python_calc PoleCalculator, per case."""

import pytest

from tests.parity.builders import build_pole_calculator, build_seismic, build_wind
from tests.parity.parity import assert_matches, case_names, load_fixture, plain


@pytest.mark.parametrize("name", case_names())
def test_wind_by_elevation(name):
    fixture = load_fixture(name)
    wind = build_wind(fixture["input"])
    expected = fixture["expected"]["wind"]
    actual = {
        "common_parameters": wind.common_parameters,
        "by_elevation": [
            {
                "elevation_m": z["elevation_m"],
                "kz": wind.kz_at(z["elevation_m"]),
                "wind_pressure_n_m2": wind.wind_pressure_at(z["elevation_m"]),
            }
            for z in expected["by_elevation"]
        ],
    }
    assert_matches(actual, expected)


@pytest.mark.parametrize("name", case_names())
def test_pole_aggregate(name):
    fixture = load_fixture(name)
    case_input = fixture["input"]
    calculator = build_pole_calculator(
        case_input, build_wind(case_input), build_seismic(case_input["seismic"])
    )
    for position in fixture["expected"]["positions"]:
        actual = plain(calculator.aggregate_at(position["evaluated_position_m"]))
        assert_matches(actual, position["pole"], f"{name}@{position['evaluated_position_m']}")


@pytest.mark.parametrize("name", case_names())
def test_pole_aggregate_without_seismic(name):
    """Deviation: same wind numbers, every seismic field None."""
    fixture = load_fixture(name)
    case_input = fixture["input"]
    calculator = build_pole_calculator(case_input, build_wind(case_input), None)
    for position in fixture["expected"]["positions"]:
        actual = plain(calculator.aggregate_at(position["evaluated_position_m"]))
        assert_matches(
            actual,
            position["pole"],
            f"{name}@{position['evaluated_position_m']}",
            seismic_absent=True,
        )