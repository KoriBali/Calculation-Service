"""Export parity fixtures (answer keys) from python_calc.

Dev-only tool. It is never imported by the app or by pytest. It runs the raw
python_calc engine on fixed inputs and writes the inputs plus every resulting
number to ``tests/parity/fixtures/*.json``. The parity tests then run the same
inputs through ``app.engine`` and require identical numbers.

Usage, from the calculation_service root:

    python tools/export_parity_fixtures.py
    python tools/export_parity_fixtures.py --python-calc /path/to/python_calc

Re-run it whenever python_calc formulas change, review the JSON diff, and
commit the fixtures together with the matching engine change.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "parity" / "fixtures"
DEFAULT_PYTHON_CALC = ROOT.parent / "python_calc"

# Files of python_calc that the fixtures depend on. manual_check.py is not
# listed: the cases below carry their own fixed input.
ENGINE_PATHS = ("BasicFunction.py", "domain", "calculation")


# ============================================================================
# FIXED INPUTS
# ============================================================================

MANUAL_CHECK_POLES = [
    {
        "name": "Pole-1",
        "pole_type": "Straight",
        "diameter_lower_mm": 75,
        "diameter_upper_mm": 75,
        "thickness_lower_mm": 4.5,
        "thickness_upper_mm": 4.5,
        "material": "STK400",
        "top_elevation_m": 8.15,
    },
    {
        "name": "Pole-2",
        "pole_type": "Taper",
        "diameter_lower_mm": 165.2,
        "diameter_upper_mm": 75,
        "thickness_lower_mm": 4.5,
        "thickness_upper_mm": 4.5,
        "material": "STK400",
        "top_elevation_m": 6.65,
    },
    {
        "name": "Pole-3",
        "pole_type": "Straight",
        "diameter_lower_mm": 165.2,
        "diameter_upper_mm": 165.2,
        "thickness_lower_mm": 4.5,
        "thickness_upper_mm": 4.5,
        "material": "STK400",
        "top_elevation_m": 1.65,
    },
]

MANUAL_CHECK_DIRECT_OBJECTS = [
    {
        "name": "DO1",
        "object_type": "Directional",
        "front_area_m2": 0.049,
        "side_area_m2": 0.041,
        "mass_per_unit_kg": 5.8,
        "elevation_m": 8.15,
        "base_wind_coefficient": 1.0,
        "quantity": 1,
        "fixed_angle_deg": 0,
    },
]

MANUAL_CHECK_OVERHEAD_WIRES = [
    {
        "name": "OHW1",
        "mass_per_length_kg_m": 0.19,
        "diameter_mm": 11.5,
        "elevation_m": 5.75,
        "span_length_m": 15,
        "sag_ratio_percent": 3,
        "base_wind_coefficient": 1.0,
        "fixed_angle_deg": 180,
        "vertical_angle_deg": 0,
    },
]

CASES = {
    "manual_check_std3": {
        "description": "manual_check.py at python_calc 41cca03: 3 segments, DO, OHW",
        "input": {
            "wind": {"design_standard": 3, "structure_height_m": 8.15},
            "seismic": {"position": "Ground", "k_value": 0.5},
            "overdesign_factor": 1.0,
            "base_elevation_m": 0.0,
            "poles": MANUAL_CHECK_POLES,
            "direct_objects": MANUAL_CHECK_DIRECT_OBJECTS,
            "overhead_wires": MANUAL_CHECK_OVERHEAD_WIRES,
            "evaluated_positions_m": [6.65, 1.65, 0.0],
        },
    },
    "manual_check_std3_no_ohw": {
        "description": "manual_check_std3 without the overhead wire (API parity before D6)",
        "input": {
            "wind": {"design_standard": 3, "structure_height_m": 8.15},
            "seismic": {"position": "Ground", "k_value": 0.5},
            "overdesign_factor": 1.0,
            "base_elevation_m": 0.0,
            "poles": MANUAL_CHECK_POLES,
            "direct_objects": MANUAL_CHECK_DIRECT_OBJECTS,
            "overhead_wires": [],
            "evaluated_positions_m": [6.65, 1.65, 0.0],
        },
    },
    "manual_check_std1": {
        "description": "manual_check geometry with standard 1 (Kz in Cf)",
        "input": {
            "wind": {
                "design_standard": 1,
                "structure_height_m": 8.15,
                "atmospheric_category": 1,
                "basic_wind_speed_m_s": 100,
            },
            "seismic": {"position": "Ground", "k_value": 0.5},
            "overdesign_factor": 1.0,
            "base_elevation_m": 0.0,
            "poles": MANUAL_CHECK_POLES,
            "direct_objects": MANUAL_CHECK_DIRECT_OBJECTS,
            "overhead_wires": MANUAL_CHECK_OVERHEAD_WIRES,
            "evaluated_positions_m": [6.65, 1.65, 0.0],
        },
    },
    "std6_rooftop_mixed": {
        "description": (
            "Standard 6, rooftop class S, overdesign 1.2, taper with different "
            "thicknesses cut mid-segment, Omni + Directional, object exactly at "
            "an evaluated position that is also a joint"
        ),
        "input": {
            "wind": {
                "design_standard": 6,
                "structure_height_m": 12.0,
                "atmospheric_category": 3,
                "basic_wind_speed_m_s": 34,
            },
            "seismic": {"position": "Rooftop", "seismic_class": "S"},
            "overdesign_factor": 1.2,
            "base_elevation_m": 0.0,
            "poles": [
                {
                    "name": "Lower",
                    "pole_type": "Taper",
                    "diameter_lower_mm": 216.3,
                    "diameter_upper_mm": 139.8,
                    "thickness_lower_mm": 6,
                    "thickness_upper_mm": 4.5,
                    "material": "STK490",
                    "top_elevation_m": 7.0,
                },
                {
                    "name": "Upper",
                    "pole_type": "Straight",
                    "diameter_lower_mm": 139.8,
                    "diameter_upper_mm": 139.8,
                    "thickness_lower_mm": 4.5,
                    "thickness_upper_mm": 4.5,
                    "material": "STK400",
                    "top_elevation_m": 12.0,
                },
            ],
            "direct_objects": [
                {
                    "name": "Lamp",
                    "object_type": "Omni",
                    "front_area_m2": 0.3,
                    "side_area_m2": 0,
                    "mass_per_unit_kg": 20,
                    "elevation_m": 12.0,
                    "base_wind_coefficient": 1.0,
                    "quantity": 2,
                    "fixed_angle_deg": 0,
                },
                {
                    "name": "Sign",
                    "object_type": "Directional",
                    "front_area_m2": 0.5,
                    "side_area_m2": 0.1,
                    "mass_per_unit_kg": 15,
                    "elevation_m": 7.0,
                    "base_wind_coefficient": 1.2,
                    "quantity": 1,
                    "fixed_angle_deg": 45,
                },
            ],
            "overhead_wires": [],
            "evaluated_positions_m": [7.0, 3.5, 0.0],
        },
    },
    "pole_only_std2": {
        "description": "Single straight segment, no equipment, base elevation above zero",
        "input": {
            "wind": {"design_standard": 2, "structure_height_m": 6.0},
            "seismic": {"position": "Ground", "k_value": 0.3},
            "overdesign_factor": 1.0,
            "base_elevation_m": 0.5,
            "poles": [
                {
                    "name": "Pole",
                    "pole_type": "Straight",
                    "diameter_lower_mm": 114.3,
                    "diameter_upper_mm": 114.3,
                    "thickness_lower_mm": 4.5,
                    "thickness_upper_mm": 4.5,
                    "material": "SGP",
                    "top_elevation_m": 6.0,
                },
            ],
            "direct_objects": [],
            "overhead_wires": [],
            "evaluated_positions_m": [0.5, 2.0],
        },
    },
}

SECTION_DIAMETERS_MM = (60.5, 75, 89.1, 114.3, 139.8, 165.2, 216.3)
SECTION_THICKNESSES_MM = (3.2, 4.5, 6)
SECTION_LENGTHS_M = (1.5, 5.0)
TAPER_SEGMENTS = (
    # (diameter_upper, diameter_lower, thickness_upper, thickness_lower, length)
    (75, 165.2, 4.5, 4.5, 5.0),
    (89.1, 139.8, 4.5, 4.5, 0.5),
    (139.8, 216.3, 4.5, 6, 7.0),
    (75, 120.1, 4.5, 4.5, 3.2),
)

WIND_HEIGHTS_M = (4.0, 8.15, 25.0, 45.0)
WIND_SPEEDS_M_S = (34, 60)
WIND_ELEVATIONS_M = (0.0, 2.0, 5.0, 8.15, 12.0, 30.0)


# ============================================================================
# EXPORT
# ============================================================================


def plain(value):
    """Dataclass result -> JSON-ready dict (tuples become lists)."""
    return json.loads(json.dumps(asdict(value), allow_nan=False))


def git_state(python_calc: Path) -> tuple[str, bool]:
    commit = subprocess.run(
        ["git", "-C", str(python_calc), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(python_calc), "status", "--porcelain", "--", *ENGINE_PATHS],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return commit, bool(dirty)


def export_sections(pc):
    BasicFunction = pc["BasicFunction"]
    straight = [
        {
            "diameter_mm": d,
            "thickness_mm": t,
            "length_m": length,
            "cross_section_area_cm2": BasicFunction.Cross_AreaP(d, t),
            "moment_of_inertia_cm4": BasicFunction.Moment_Inertia(d, t),
            "section_modulus_cm3": BasicFunction.Section_Modulus(d, t),
            "radius_of_gyration_cm": BasicFunction.Radius_Gyration(d, t),
            "straight_pole_mass_kg": BasicFunction.Pole_WeightKg_Straight(d, t, length),
        }
        for d in SECTION_DIAMETERS_MM
        for t in SECTION_THICKNESSES_MM
        for length in SECTION_LENGTHS_M
    ]
    taper = [
        {
            "diameter_upper_mm": du,
            "diameter_lower_mm": dl,
            "thickness_upper_mm": tu,
            "thickness_lower_mm": tl,
            "length_m": length,
            "taper_pole_mass_kg": BasicFunction.Pole_WeightKg_Taper(du, dl, tu, tl, length),
        }
        for du, dl, tu, tl, length in TAPER_SEGMENTS
    ]
    return {"straight": straight, "taper": taper}


def export_conditions(pc):
    WindCondition = pc["WindCondition"]
    SeismicCondition = pc["SeismicCondition"]
    MATERIALS = pc["MATERIALS"]

    wind_inputs = [
        {"design_standard": std, "structure_height_m": 8.15}
        for std in (2, 3, 4, 5)
    ] + [
        {
            "design_standard": std,
            "structure_height_m": height,
            "atmospheric_category": adc,
            "basic_wind_speed_m_s": speed,
        }
        for std in (1, 6)
        for adc in (1, 2, 3, 4)
        for height in WIND_HEIGHTS_M
        for speed in WIND_SPEEDS_M_S
    ]
    wind = []
    for wind_input in wind_inputs:
        condition = WindCondition(**wind_input)
        wind.append({
            "input": wind_input,
            "common_parameters": condition.common_parameters,
            "by_elevation": [
                {
                    "elevation_m": z,
                    "kz": condition.kz_at(z),
                    "wind_pressure_n_m2": condition.wind_pressure_at(z),
                }
                for z in WIND_ELEVATIONS_M
            ],
        })

    seismic_inputs = [
        {"position": "Ground", "k_value": k} for k in (0.3, 0.5, 1.0)
    ] + [
        {"position": "Rooftop", "seismic_class": c} for c in ("A", "B", "S", "s")
    ]
    seismic = []
    for seismic_input in seismic_inputs:
        condition = build_seismic(SeismicCondition, seismic_input)
        seismic.append({
            "input": seismic_input,
            "position": condition.position,
            "k_value": condition.k_value,
            "seismic_class": condition.seismic_class,
        })

    return {
        "wind": wind,
        "seismic": seismic,
        "materials": [plain(material) for material in MATERIALS.values()],
    }


def build_seismic(SeismicCondition, seismic_input):
    if seismic_input["position"] == "Ground":
        return SeismicCondition.ground(seismic_input["k_value"])
    return SeismicCondition.rooftop(seismic_input["seismic_class"])


def export_case(pc, case_input):
    wind = pc["WindCondition"](**case_input["wind"])
    seismic = build_seismic(pc["SeismicCondition"], case_input["seismic"])
    poles = [pc["PoleObject"](**pole) for pole in case_input["poles"]]
    pole_calculator = pc["PoleCalculator"](
        assembly=pc["PoleAssembly"](poles, base_elevation_m=case_input["base_elevation_m"]),
        wind_condition=wind,
        seismic_condition=seismic,
        overdesign_factor=pc["OverdesignFactor"](case_input["overdesign_factor"]),
    )
    direct_object_calculator = (
        pc["DirectObjectCalculator"](
            [pc["DirectObject"](**item) for item in case_input["direct_objects"]],
            wind,
            seismic,
        )
        if case_input["direct_objects"]
        else None
    )
    overhead_wire_calculator = (
        pc["OverheadWireCalculator"](
            [pc["OverheadWire"](**item) for item in case_input["overhead_wires"]],
            wind,
            seismic,
        )
        if case_input["overhead_wires"]
        else None
    )
    section_check = pc["EvaluatedPositionCalculator"](
        pole_calculator,
        direct_object_calculator,
        overhead_wire_calculator,
    )

    elevations = sorted({
        *(pole["top_elevation_m"] for pole in case_input["poles"]),
        *(item["elevation_m"] for item in case_input["direct_objects"]),
        *(item["elevation_m"] for item in case_input["overhead_wires"]),
    })
    positions = []
    for position in case_input["evaluated_positions_m"]:
        positions.append({
            "evaluated_position_m": position,
            "pole": plain(pole_calculator.aggregate_at(position)),
            "direct_object": (
                None if direct_object_calculator is None
                else plain(direct_object_calculator.aggregate_at(position))
            ),
            "overhead_wire": (
                None if overhead_wire_calculator is None
                else plain(overhead_wire_calculator.aggregate_at(position))
            ),
            "section_check": plain(section_check.calculate_at(position)),
        })

    return {
        "wind": {
            "common_parameters": wind.common_parameters,
            "by_elevation": [
                {
                    "elevation_m": z,
                    "kz": wind.kz_at(z),
                    "wind_pressure_n_m2": wind.wind_pressure_at(z),
                }
                for z in elevations
            ],
        },
        "positions": positions,
    }


def load_python_calc(python_calc: Path) -> dict:
    sys.path.insert(0, str(python_calc))
    import BasicFunction
    from calculation.direct_object_calculator import DirectObjectCalculator
    from calculation.evaluated_position_calculator import EvaluatedPositionCalculator
    from calculation.overhead_wire_calculator import OverheadWireCalculator
    from calculation.pole_assembly import PoleAssembly
    from calculation.pole_calculator import PoleCalculator
    from domain.conditions import SeismicCondition, WindCondition
    from domain.direct_object import DirectObject
    from domain.loads import OverdesignFactor
    from domain.materials import MATERIALS
    from domain.overhead_wire import OverheadWire
    from domain.pole import PoleObject

    return {
        "BasicFunction": BasicFunction,
        "DirectObjectCalculator": DirectObjectCalculator,
        "EvaluatedPositionCalculator": EvaluatedPositionCalculator,
        "OverheadWireCalculator": OverheadWireCalculator,
        "PoleAssembly": PoleAssembly,
        "PoleCalculator": PoleCalculator,
        "SeismicCondition": SeismicCondition,
        "WindCondition": WindCondition,
        "DirectObject": DirectObject,
        "OverdesignFactor": OverdesignFactor,
        "MATERIALS": MATERIALS,
        "OverheadWire": OverheadWire,
        "PoleObject": PoleObject,
    }


def write(name: str, meta: dict, body: dict) -> None:
    path = FIXTURE_DIR / f"{name}.json"
    path.write_text(
        json.dumps({"meta": meta, **body}, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--python-calc", type=Path, default=DEFAULT_PYTHON_CALC)
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="export even if python_calc engine files have uncommitted changes",
    )
    args = parser.parse_args()

    python_calc = args.python_calc.resolve()
    if not (python_calc / "BasicFunction.py").is_file():
        parser.error(f"python_calc not found at {python_calc}")

    commit, dirty = git_state(python_calc)
    if dirty and not args.allow_dirty:
        parser.error(
            "python_calc engine files have uncommitted changes; commit them "
            "first or pass --allow-dirty (fixtures would not be reproducible)"
        )

    pc = load_python_calc(python_calc)
    meta = {
        "source": "python_calc",
        "python_calc_commit": commit,
        "python_calc_dirty": dirty,
        "generator": "tools/export_parity_fixtures.py",
    }

    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    write("sections", meta, export_sections(pc))
    write("conditions", meta, export_conditions(pc))
    for name, case in CASES.items():
        write(f"case_{name}", meta, {
            "description": case["description"],
            "input": case["input"],
            "expected": export_case(pc, case["input"]),
        })
    return 0


if __name__ == "__main__":
    sys.exit(main())