"""The module providing Pydantic models for datetime specifications."""

from datetime import datetime, timedelta
from typing import Any

from pydantic import PastDatetime, field_validator, model_validator

from monkey_wrench.date_time import assert_start_precedes_end
from monkey_wrench.task.models.specifications.base import Specifications


def validate_datetime(value: list) -> datetime:
    if not isinstance(value, list):
        raise ValueError("datetime must be a list")

    for v in value:
        if not isinstance(v, int):
            raise ValueError("Items in a datetime list must be integer.")
        if v < 0:
            raise ValueError("Items in a datetime list must be positive.")

    return datetime(*value)


class StartDateTime(Specifications):
    start_datetime: PastDatetime

    # noinspection PyNestedDecorators
    @field_validator("start_datetime", mode="before")
    @classmethod
    def validate_start_datetime(cls, value: Any) -> datetime:
        return validate_datetime(value)


class EndDateTime(Specifications):
    end_datetime: PastDatetime

    # noinspection PyNestedDecorators
    @field_validator("end_datetime", mode="before")
    @classmethod
    def validate_end_datetime(cls, value: Any) -> datetime:
        return validate_datetime(value)


class DateTimeRange(StartDateTime, EndDateTime):
    # noinspection PyNestedDecorators
    @model_validator(mode="after")
    @classmethod
    def validate_start_datetime_before_end_datetime(cls, value: Any) -> Any:
        assert_start_precedes_end(value.start_datetime, value.end_datetime)
        return value


class DateTimeRangeInBatches(DateTimeRange):
    batch_interval: timedelta

    # noinspection PyNestedDecorators
    @field_validator("batch_interval", mode="before")
    @classmethod
    def validate_batch_interval(cls, value: dict[str, int]) -> timedelta:
        return timedelta(**value)
