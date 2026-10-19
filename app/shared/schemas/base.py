from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Base for every request schema.

    - JSON keys are camelCase (``topElevationM``); snake_case is accepted too,
      because gateway ``forward()`` sends ``model_dump()`` in snake_case.
    - Unknown keys are rejected (422), so a typo never turns into a silent
      default and fields not opened yet (e.g. ``overheadWires``) are refused.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        extra="forbid",
        frozen=True,
    )