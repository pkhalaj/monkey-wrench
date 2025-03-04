"""The package providing all datetime utilities."""

from ._common import (
    assert_datetime_has_past,
    assert_datetime_is_timezone_aware,
    assert_start_precedes_end,
    floor_datetime_minutes_to_specific_snapshots,
    number_of_days_in_month,
)
from ._parser import ChimpFilePathParser, DateTimeParser, DateTimeParserBase, SeviriIDParser
from ._types import Day, Hour, Minute, Minutes, Month, Year
from .models import (
    AwarePastDateTime,
    DateTimePeriod,
    DateTimePeriodStrict,
    DateTimeRange,
    DateTimeRangeInBatches,
    EndDateTime,
    StartDateTime,
    TimeDeltaDict,
    TimeInterval,
)

__all__ = [
    "AwarePastDateTime",
    "ChimpFilePathParser",
    "DateTimeParser",
    "DateTimeParserBase",
    "DateTimePeriod",
    "DateTimePeriodStrict",
    "DateTimeRange",
    "DateTimeRangeInBatches",
    "Day",
    "EndDateTime",
    "Hour",
    "Minute",
    "Minutes",
    "Month",
    "SeviriIDParser",
    "StartDateTime",
    "TimeDeltaDict",
    "TimeInterval",
    "Year",
    "assert_datetime_has_past",
    "assert_datetime_is_timezone_aware",
    "assert_start_precedes_end",
    "floor_datetime_minutes_to_specific_snapshots",
    "number_of_days_in_month"
]
