"""Helpers for parity tests: load python_calc fixtures and compare numbers."""

import json
import math
from dataclasses import asdict
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"
TOLERANCE = 1e-9


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / f"{name}.json").read_text(encoding="utf-8"))


def case_names() -> list[str]:
    return sorted(path.stem for path in FIXTURE_DIR.glob("case_*.json"))


def plain(result) -> dict:
    """Engine dataclass -> the same JSON shape the fixture generator writes."""
    return json.loads(json.dumps(asdict(result), allow_nan=False))


def assert_matches(actual, expected, path: str = "$", seismic_absent: bool = False):
    """Recursively require ``actual`` to equal ``expected``.

    Numbers may differ by at most TOLERANCE. With ``seismic_absent=True`` every
    key containing "seismic" must be None in ``actual`` (engine deviation: no
    seismic input means no seismic result), and all other keys still match.
    """
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected object, got {actual!r}"
        assert actual.keys() == expected.keys(), (
            f"{path}: keys differ: {sorted(actual.keys() ^ expected.keys())}"
        )
        for key in expected:
            child = f"{path}.{key}"
            if seismic_absent and "seismic" in key.lower():
                assert actual[key] is None, f"{child}: expected None, got {actual[key]!r}"
                continue
            assert_matches(actual[key], expected[key], child, seismic_absent)
    elif isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: expected list, got {actual!r}"
        assert len(actual) == len(expected), f"{path}: length {len(actual)} != {len(expected)}"
        for index, (a, e) in enumerate(zip(actual, expected)):
            assert_matches(a, e, f"{path}[{index}]", seismic_absent)
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        assert isinstance(actual, (int, float)) and not isinstance(actual, bool), (
            f"{path}: expected number, got {actual!r}"
        )
        assert math.isclose(actual, expected, rel_tol=0, abs_tol=TOLERANCE), (
            f"{path}: {actual!r} != {expected!r}"
        )
    else:
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"