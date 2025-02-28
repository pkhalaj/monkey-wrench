from datetime import datetime, timedelta
from typing import Literal, Self

from pydantic import AfterValidator, AwareDatetime, Field, model_validator
from typing_extensions import Annotated

from monkey_wrench.date_time._common import assert_datetime_has_past
from monkey_wrench.generic import Model, assert_

AwarePastDateTime = Annotated[AwareDatetime, AfterValidator(lambda dt: assert_datetime_has_past(dt) and dt)]
"""Type annotation and validator for a time-zone aware ``datetime`` object, which has past."""

TimeDeltaDict = Annotated[
    dict[Literal["weeks", "days", "hours", "minutes", "seconds"], float],
    Field(min_length=1, max_length=5),
    AfterValidator(lambda dct: timedelta(**dct))
]
"""Type annotation and validator for a ``timedelta`` object, given as a dictionary."""

TimeInterval = timedelta | TimeDeltaDict
"""Type alias for a time interval, given both as a ``timedelta`` or as a :class:`TimeDeltaDict`."""


class StartDateTime(Model):
    start_datetime: AwarePastDateTime | None = None


class EndDateTime(Model):
    end_datetime: AwarePastDateTime | None = None


class DateTimePeriod(StartDateTime, EndDateTime):

    @property
    def datetime_period(self) -> "DateTimePeriod":
        return DateTimePeriod(start_datetime=self.start_datetime, end_datetime=self.end_datetime)

    @property
    def span(self) -> timedelta:
        """Return the span between the start and end datetimes."""
        self.assert_datetime_instances_are_not_none()
        return self.end_datetime - self.start_datetime

    def as_tuple(self, sort: bool = False) -> tuple[datetime, datetime]:
        """Return the datetime period as a 2-tuple.

        Args:
            sort:
                Determines whether the returned tuple should be first sorted or not. Defaults to ``False``. If it is set
                to ``True``, the first element of the 2-tuple is always the minimum of the ``start_datetime`` and
                ``end_datetime``.

        Returns:
            The datetime period as a 2-tuple.
        """
        start, end = self.start_datetime, self.end_datetime
        if sort:
            start, end = min(start, end), max(start, end)
        return start, end

    def assert_both_or_neither_datetime_instances_are_none(self):
        """Assert that if one of the datetime instances is ``None``, the other one is also ``None``."""
        assert_(
            self.as_tuple().count(None) != 1,
            "Both the start and the end datetime must be None, if one of them is `None`.",
            silent=False
        )

    def assert_datetime_instances_are_not_none(self):
        """Assert that none of the datetime instances are ``None``."""
        assert_(
            None not in self.as_tuple(),
            "The start and the end datetime must not be `None`.",
            silent=False
        )


class DateTimePeriodStrict(DateTimePeriod):
    """Same as :obj:`DateTimePeriod` but does not allow fields to have ``None`` values."""

    @model_validator(mode="after")
    def validate_datetime_instances(self) -> Self:  # noqa: N804
        """Ensure that datetime instances are not ``None``."""
        self.assert_datetime_instances_are_not_none()
        return self
