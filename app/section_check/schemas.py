from typing import Annotated

from pydantic import Field, PositiveFloat, model_validator

from app.shared.schemas.base import ApiModel
from app.shared.schemas.conditions import SeismicInput, WindInput
from app.shared.schemas.direct_object import DirectObjectInput
from app.shared.schemas.pole import PoleSegmentInput


class SectionCheckRequest(ApiModel):
    """Every component except the pole is optional: sent = calculated.

    ``overheadWires`` is not accepted yet (waits for decision D6).
    """

    wind: WindInput
    seismic: SeismicInput | None = None
    overdesign_factor: PositiveFloat = 1.0
    base_elevation_m: float = 0.0
    poles: Annotated[list[PoleSegmentInput], Field(min_length=1)]
    direct_objects: list[DirectObjectInput] = Field(default_factory=list)
    evaluated_positions_m: Annotated[list[float], Field(min_length=1)]

    @model_validator(mode="after")
    def _check_consistency(self):
        for label, items in (("poles", self.poles), ("directObjects", self.direct_objects)):
            names = [item.name for item in items]
            if len(names) != len(set(names)):
                raise ValueError(f"{label}: name must be unique")

        positions = self.evaluated_positions_m
        if len(positions) != len(set(positions)):
            raise ValueError("evaluatedPositionsM: positions must be unique")
        if any(position < self.base_elevation_m for position in positions):
            raise ValueError("evaluatedPositionsM: position cannot be below baseElevationM")
        return self
