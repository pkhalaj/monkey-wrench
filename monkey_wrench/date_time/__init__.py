"""The package providing all datetime utilities."""

from ._batch import datetime_range, generate_datetime_batches
from ._common import (
    assert_start_precedes_end,
    floor_datetime_minutes_to_specific_snapshots,
    number_of_days_in_month,
)
from ._parser import DateTimeParser, DateTimeParserBase, FilePathParser, SeviriIDParser
from ._types import Minute, Minutes

__all__ = [
    "DateTimeParser",
    "DateTimeParserBase",
    "FilePathParser",
    "Minute",
    "Minutes",
    "SeviriIDParser",
    "assert_start_precedes_end",
    "datetime_range",
    "floor_datetime_minutes_to_specific_snapshots",
    "generate_datetime_batches",
    "number_of_days_in_month"
]
