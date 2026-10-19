"""Parity: engine Direct Object and overhead wire calculators == python_calc."""

import pytest

from tests.parity.builders import (
    build_direct_object_calculator,
    build_overhead_wire_calculator,
    build_seismic,
    build_wind,
)
from tests.parity.parity import assert_matches, case_names, load_fixture, plain

COMPONENTS = {
    "direct_object": build_direct_object_calculator,
    "overhead_wire": build_overhead_wire_calculator,
}


@pytest.mark.parametrize("seismic_absent", [False, True], ids=["seismic", "no-seismic"])
@pytest.mark.parametrize("component", sorted(COMPONENTS))
@pytest.mark.parametrize("name", case_names())
def test_component_aggregate(name, component, seismic_absent):
    fixture = load_fixture(name)
    case_input = fixture["input"]
    seismic = None if seismic_absent else build_seismic(case_input["seismic"])
    calculator = COMPONENTS[component](case_input, build_wind(case_input), seismic)

    for position in fixture["expected"]["positions"]:
        expected = position[component]
        label = f"{name}@{position['evaluated_position_m']}.{component}"
        if expected is None:
            assert calculator is None, label
            continue
        actual = plain(calculator.aggregate_at(position["evaluated_position_m"]))
        assert_matches(actual, expected, label, seismic_absent=seismic_absent)