"""Parity: engine conditions and materials == python_calc domain."""

import pytest

from app.engine.conditions.wind import WindCondition
from app.engine.materials import MATERIALS
from tests.parity.builders import build_seismic
from tests.parity.parity import assert_matches, load_fixture, plain

FIXTURE = load_fixture("conditions")


@pytest.mark.parametrize("row", FIXTURE["wind"], ids=lambda row: str(row["input"]))
def test_wind_condition(row):
    condition = WindCondition(**row["input"])
    actual = {
        "input": row["input"],
        "common_parameters": condition.common_parameters,
        "by_elevation": [
            {
                "elevation_m": z["elevation_m"],
                "kz": condition.kz_at(z["elevation_m"]),
                "wind_pressure_n_m2": condition.wind_pressure_at(z["elevation_m"]),
            }
            for z in row["by_elevation"]
        ],
    }
    assert_matches(actual, row)


@pytest.mark.parametrize("row", FIXTURE["seismic"], ids=lambda row: str(row["input"]))
def test_seismic_condition(row):
    condition = build_seismic(row["input"])
    actual = {
        "input": row["input"],
        "position": condition.position,
        "k_value": condition.k_value,
        "seismic_class": condition.seismic_class,
    }
    assert_matches(actual, row)


def test_materials():
    assert_matches([plain(material) for material in MATERIALS.values()], FIXTURE["materials"])
