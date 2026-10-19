"""Regression tests comparing Python helpers with M_Func_Basic.bas.

Ported from python_calc ``tests/test_basic_function.py``.
"""

import unittest

from app.engine import sections


class BasicFunctionTests(unittest.TestCase):
    def test_moment_of_inertia_uses_cm4_conversion(self):
        diameter = 200
        thickness = 5
        expected = round(
            (sections.PI / 64)
            * (diameter**4 - (diameter - 2 * thickness) ** 4)
            / 10000,
            2,
        )

        self.assertEqual(
            sections.moment_of_inertia_cm4(diameter, thickness),
            expected,
        )

    def test_straight_pole_mass_is_rounded_to_two_decimals(self):
        raw_mass = (
            sections.PI
            / 4
            * (200**2 - (200 - 2 * 5) ** 2)
            / 10**6
            * sections.DENSITY
            * 5
        )

        self.assertEqual(
            sections.straight_pole_mass_kg(200, 5, 5),
            round(raw_mass, 2),
        )

    def test_tapered_pole_mass_is_rounded_to_two_decimals(self):
        diameter_upper = 200
        diameter_lower = 300
        thickness_upper = 4
        thickness_lower = 6
        length = 10
        raw_mass = (
            sections.PI
            * length
            / 4
            * (
                ((diameter_lower - diameter_upper) / 2 + diameter_upper) ** 2
                - (
                    (
                        (diameter_lower - 2 * thickness_lower)
                        - (diameter_upper - 2 * thickness_upper)
                    )
                    / 2
                    + (diameter_upper - 2 * thickness_upper)
                )
                ** 2
            )
            / 10**6
            * sections.DENSITY
        )
        mass = sections.taper_pole_mass_kg(
            diameter_upper_mm=diameter_upper,
            diameter_lower_mm=diameter_lower,
            thickness_upper_mm=thickness_upper,
            thickness_lower_mm=thickness_lower,
            length_m=length,
        )

        self.assertEqual(mass, round(raw_mass, 2))


if __name__ == "__main__":
    unittest.main()
