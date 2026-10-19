"""The eight wind directions evaluated by the engine.

Ported from python_calc ``domain/conditions.py`` (commit 41cca03). The order
N, S, E, W, NE, SW, NW, SE is part of the result contract.
"""

from dataclasses import dataclass
from math import pi


@dataclass(frozen=True)
class WindDirection:
    """Named wind direction and its angle in radians."""

    name: str
    angle_rad: float


WIND_DIRECTIONS: tuple[WindDirection, ...] = (
    WindDirection("N", pi * 2 / 4),
    WindDirection("S", pi * 6 / 4),
    WindDirection("E", pi * 0 / 4),
    WindDirection("W", pi * 4 / 4),
    WindDirection("NE", pi * 1 / 4),
    WindDirection("SW", pi * 5 / 4),
    WindDirection("NW", pi * 3 / 4),
    WindDirection("SE", pi * 7 / 4),
)
