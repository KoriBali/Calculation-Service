from dataclasses import dataclass

@dataclass
class PoleInput:
    material_pole : str       # e.g. "STK400"
    lowest_height_pole: float # meter
    height_pole: float        # meter
    thickness_pole: float     # mm
    diameter_pole: float      # mm

    def __post_init__(self):
        if self.thickness_pole >= self.diameter_pole / 2:
            raise ValueError(
                f"thickness_pole ({self.thickness_pole}mm) must be less than "
                f"half of diameter_pole ({self.diameter_pole / 2}mm)"
            )
        if self.height_pole <= 0:
            raise ValueError("height_pole must be greater than 0")
        if self.diameter_pole <= 0:
            raise ValueError("diameter_pole must be greater than 0")
        if self.thickness_pole <= 0:
            raise ValueError("thickness_pole must be greater than 0")




@dataclass
class ObjectInput:
    name_do: str
    weight_do: float          # kg
    height_do: float          # meter (mounting height from ground)
    cf_do: float              # coefficient
    area_side_do: float       # m²
    area_front_do: float      # m²
 