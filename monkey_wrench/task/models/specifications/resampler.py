"""The module providing Pydantic models for resampler specifications."""

from pathlib import Path
from typing import Any, Literal

from pydantic import ConfigDict, FilePath, NonNegativeInt, field_validator
from pyresample import area_config, load_area

from monkey_wrench.input_output import AbsolutePath
from monkey_wrench.task.models.specifications.base import Specifications


class Resampler(Specifications):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    area: AbsolutePath[FilePath] | dict[str, Any]
    radius_of_influence: NonNegativeInt = 20000
    cache: Literal["filecache", "blockcache"] | None = None

    # noinspection PyNestedDecorators
    @field_validator("area", mode="after")
    @classmethod
    def validate_and_load_area(cls, value: Any) -> Any:
        match value.area:
            case dict():
                value.area = area_config._create_area_def_from_dict(value.pop("area_name"), value)
            case Path():
                value.area = load_area(value)
            case _:
                raise ValueError(f"Invalid area type: {type(value)}")
        return value
