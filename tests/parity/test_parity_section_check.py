"""Parity: engine section check == python_calc EvaluatedPositionCalculator."""

import pytest

from tests.parity.builders import build_section_check
from tests.parity.parity import assert_matches, case_names, load_fixture, plain


@pytest.mark.parametrize("seismic_absent", [False, True], ids=["seismic", "no-seismic"])
@pytest.mark.parametrize("name", case_names())
def test_section_check(name, seismic_absent):
    fixture = load_fixture(name)
    calculator = build_section_check(fixture["input"], seismic_absent=seismic_absent)
    for position in fixture["expected"]["positions"]:
        actual = plain(calculator.calculate_at(position["evaluated_position_m"]))
        assert_matches(
            actual,
            position["section_check"],
            f"{name}@{position['evaluated_position_m']}",
            seismic_absent=seismic_absent,
        )