"""Parity: engine.sections == python_calc BasicFunction."""

import pytest

from app.engine import sections
from tests.parity.parity import assert_matches, load_fixture

FIXTURE = load_fixture("sections")


@pytest.mark.parametrize("row", FIXTURE["straight"])
def test_straight_section_and_mass(row):
    d, t, length = row["diameter_mm"], row["thickness_mm"], row["length_m"]
    actual = {
        **{key: row[key] for key in ("diameter_mm", "thickness_mm", "length_m")},
        "cross_section_area_cm2": sections.cross_section_area_cm2(d, t),
        "moment_of_inertia_cm4": sections.moment_of_inertia_cm4(d, t),
        "section_modulus_cm3": sections.section_modulus_cm3(d, t),
        "radius_of_gyration_cm": sections.radius_of_gyration_cm(d, t),
        "straight_pole_mass_kg": sections.straight_pole_mass_kg(d, t, length),
    }
    assert_matches(actual, row)


@pytest.mark.parametrize("row", FIXTURE["taper"])
def test_taper_mass(row):
    actual = sections.taper_pole_mass_kg(
        row["diameter_upper_mm"],
        row["diameter_lower_mm"],
        row["thickness_upper_mm"],
        row["thickness_lower_mm"],
        row["length_m"],
    )
    assert_matches(actual, row["taper_pole_mass_kg"])