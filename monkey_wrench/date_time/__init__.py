"""The package providing all datetime utilities."""

from ._common import (
    assert_datetime_has_past,
    assert_datetime_is_timezone_aware,
    assert_start_precedes_end,
    floor_datetime_minutes_to_specific_snapshots,
    number_of_days_in_month,
)
from ._parser import DateTimeParser, DateTimeParserBase, FilePathParser, SeviriIDParser
from ._types import Minute, Minutes
from .models import (
    DateTime,
    DateTimeDict,
    DateTimeList,
    DateTimePeriod,
    DateTimeRange,
    DateTimeRangeInBatches,
    EndDateTime,
    PastDateTime,
    StartDateTime,
    TimeDeltaDict,
    TimeInterval,
    ZoneInfo_,
)

__all__ = [
    "DateTime",
    "DateTimeDict",
    "DateTimeList",
    "DateTimeParser",
    "DateTimeParserBase",
    "DateTimePeriod",
    "DateTimeRange",
    "DateTimeRangeInBatches",
    "EndDateTime",
    "FilePathParser",
    "Minute",
    "Minutes",
    "PastDateTime",
    "SeviriIDParser",
    "StartDateTime",
    "TimeDeltaDict",
    "TimeInterval",
    "ZoneInfo_",
    "assert_datetime_has_past",
    "assert_datetime_is_timezone_aware",
    "assert_start_precedes_end",
    "floor_datetime_minutes_to_specific_snapshots",
    "number_of_days_in_month"
]
