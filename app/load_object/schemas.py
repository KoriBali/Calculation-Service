from dataclasses import dataclass, field
from typing import List


@dataclass
class PoleInput:
    name: str
    diameter: float       # mm
    thickness: float      # mm
    material: str         # e.g. "STK400"
    z_height: float       # m — top of this pole segment

    def __post_init__(self):
        if self.diameter <= 0:
            raise ValueError("diameter must be greater than 0")
        if self.thickness <= 0:
            raise ValueError("thickness must be greater than 0")
        if self.thickness >= self.diameter / 2:
            raise ValueError(
                f"thickness ({self.thickness}mm) must be less than "
                f"half of diameter ({self.diameter / 2}mm)"
            )
        if self.z_height <= 0:
            raise ValueError("z_height must be greater than 0")


@dataclass
class DirectObjectInput:
    name: str
    area: float           # m²
    cf: float             # force coefficient
    weight: float         # kg
    z_height: float       # m — mounting height from ground

    def __post_init__(self):
        if self.area <= 0:
            raise ValueError(f"area for '{self.name}' must be greater than 0")
        if self.z_height <= 0:
            raise ValueError(f"z_height for '{self.name}' must be greater than 0")
        

# OverheadWire
@dataclass
class OverheadWireInput:
    name: str
    weight: float
    diameter:float
    z_height: float
    span: float
    sagging_ratio: float
    nnc: float
    fix_angle: float
    vertical_angle: float


@dataclass
class LoadObjectRequest:
    poles: List[PoleInput]
    high_evaluation: dict                                                          
    direct_objects: List[DirectObjectInput] = field(default_factory=list)  # opsional
    overhead_wires: List[OverheadWireInput] = field(default_factory=list)  # opsional


    def __post_init__(self):
        if not self.poles:
            raise ValueError("'poles' must contain at least one pole")
        if not self.high_evaluation:
            raise ValueError("'high_evaluation' must contain at least one high evaluation")
        for name, z in self.high_evaluation.items():
            if not isinstance(z, (int, float)):
                raise ValueError(f"high evaluation '{name}': z_ref must be a number")
            if float(z) < 0:
                raise ValueError(f"high evaluation '{name}': z_ref must be >= 0")
            

