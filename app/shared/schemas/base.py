from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    """Base for every request schema.

    - JSON keys are snake_case (``top_elevation_m``), the same shape gateway
      ``forward()`` sends with ``model_dump()``. camelCase is the gateway's job.
    - Unknown keys are rejected (422), so a typo or a camelCase key never turns
      into a silent default and fields not opened yet (e.g. ``overhead_wires``)
      are refused.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )
