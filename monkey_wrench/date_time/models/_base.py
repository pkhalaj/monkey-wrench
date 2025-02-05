"""The module providing Pydantic base classes for the `date_time` package."""

import datetime as datetime_
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import AfterValidator, Field, NonNegativeInt, validate_call
from typing_extensions import Annotated

from monkey_wrench.date_time._common import assert_datetime_has_past, assert_datetime_is_timezone_aware
from monkey_wrench.generic import Model

DateTimeList = Annotated[
    list[NonNegativeInt],
    Field(min_length=3, max_length=7)
]
"""Type annotation and validator for a naive ``datetime`` object, given as a list of non-negative integers."""

ZoneInfo_ = Annotated[str | ZoneInfo, AfterValidator(lambda x: x if isinstance(x, ZoneInfo) else ZoneInfo(x))]
"""Type annotation and validator for a ``ZoneInfo`` object, given as a string."""


class DateTimeDict(Model):
    """Pydantic model for timezone-aware ``datetime`` objects, given as a dictionary."""
    datetime: DateTimeList
    timezone: ZoneInfo_ = ZoneInfo("UTC")

    @property
    def timezone_aware_datetime(self) -> datetime_.datetime:
        """Return the timezone-aware datetime object from a naive datetime object."""
        return datetime_.datetime(*self.datetime, tzinfo=self.timezone)


@validate_call
def _parse(x: DateTimeDict | datetime_.datetime) -> datetime_.datetime:
    """Parse the given object into a timezone-aware datetime object."""
    if isinstance(x, DateTimeDict):
        return x.timezone_aware_datetime
    assert_datetime_is_timezone_aware(x, silent=False)
    return x


DateTime = Annotated[DateTimeDict | datetime_.datetime, AfterValidator(_parse)]
"""Type annotation and validator for a time-zone aware ``datetime`` object."""

PastDateTime = Annotated[
    DateTime,
    AfterValidator(lambda dt: assert_datetime_has_past(dt) and dt)
]
"""Type annotation and validator for a past datetime."""

TimeDeltaDict = Annotated[
    dict[Literal["weeks", "days", "hours", "minutes", "seconds"], float],
    Field(min_length=1, max_length=5),
    AfterValidator(lambda dct: datetime_.timedelta(**dct))
]
"""Type annotation and validator for a ``timedelta`` object, given as a dictionary."""

TimeInterval = datetime_.timedelta | TimeDeltaDict
"""Type alias for a time interval, given both as a ``timedelta`` or as a :class:`TimeDeltaDict`."""


class StartDateTime(Model):
    """Pydantic model for the start of a datetime period."""
    start_datetime: PastDateTime


class EndDateTime(Model):
    """Pydantic model for the end of a datetime period."""
    end_datetime: PastDateTime


class DateTimePeriod(StartDateTime, EndDateTime):
    """Pydantic model for a datetime period."""

    @property
    def span(self) -> datetime_.timedelta:
        """Return the span between start and end datetimes."""
        return self.end_datetime - self.start_datetime

    def as_tuple(self, sort: bool = False) -> tuple[datetime_.datetime, datetime_.datetime]:
        """Return the datetime period as a 2-tuple.

        Args:
            sort:
                Determines whether the returned tuple should be first sorted or not. Defaults to ``False``. If it is set
                to ``False``, the first element of the 2-tuple is always the minimum of the ``start_datetime`` and
                ``end_datetime``.

        Returns:
            The datetime period as a 2-tuple.
        """
        start, end = self.start_datetime, self.end_datetime
        if sort:
            start, end = min(start, end), max(start, end)
        return start, end
