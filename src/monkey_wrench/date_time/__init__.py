"""The package which provides datetime utilities."""

from ._batch import datetime_range, generate_datetime_batches
from ._common import (
    Order,
    assert_start_time_is_before_end_time,
    floor_datetime_minutes_to_snapshots,
    number_of_days_in_month,
)
from ._parser import DateTimeParser, FilenameParser, SeviriIDParser

__all__ = [
    "assert_start_time_is_before_end_time",
    "datetime_range",
    "DateTimeParser",
    "FilenameParser",
    "floor_datetime_minutes_to_snapshots",
    "generate_datetime_batches",
    "number_of_days_in_month",
    "Order",
    "SeviriIDParser"
]
