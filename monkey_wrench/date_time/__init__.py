"""The package providing all datetime utilities."""

from ._batch import datetime_range, generate_datetime_batches
from ._common import (
    assert_start_time_is_before_end_time,
    floor_datetime_minutes_to_specific_snapshots,
    number_of_days_in_month,
)
from ._parser import DateTimeParser, FilePathParser, SeviriIDParser
from ._types import Minute

__all__ = [
    "DateTimeParser",
    "FilePathParser",
    "Minute",
    "SeviriIDParser",
    "assert_start_time_is_before_end_time",
    "datetime_range",
    "floor_datetime_minutes_to_specific_snapshots",
    "generate_datetime_batches",
    "number_of_days_in_month"
]
