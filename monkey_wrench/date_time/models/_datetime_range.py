"""The module providing the ``DateTimeRange`` model."""

from copy import deepcopy
from datetime import datetime
from typing import Generator

from monkey_wrench.date_time.models._base import DateTimePeriod, TimeInterval


class DateTimeRange(DateTimePeriod):
    """Pydantic model for datetime ranges.

    Note:
        This can be used both as a model and also as a generator. See the examples below.

    Example:
        >>> from datetime import UTC, datetime, timedelta
        >>>
        >>> # as a data model
        >>> dt_range = DateTimeRange(
        ...  start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  end_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...  interval=timedelta(days=2)
        ... )
        >>> dt_range.start_datetime
        datetime.datetime(2022, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
        >>> dt_range.end_datetime
        datetime.datetime(2022, 1, 8, 0, 0, tzinfo=datetime.timezone.utc)
        >>> dt_range.interval
        datetime.timedelta(days=2)

        >>> # as a generator with a positive interval
        >>> dt_range = DateTimeRange(
        ...  start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  end_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...  interval=timedelta(days=2)
        ... )
        >>> for datetime_instance in dt_range:
        ...     print(datetime_instance.isoformat())
        2022-01-01T00:00:00+00:00
        2022-01-03T00:00:00+00:00
        2022-01-05T00:00:00+00:00
        2022-01-07T00:00:00+00:00

        >>> # Negative interval
        >>> dt_range = DateTimeRange(
        ...  start_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...  end_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  interval=timedelta(days=-2)
        ... )
        >>> for datetime_instance in dt_range:
        ...     print(datetime_instance.isoformat())
        2022-01-08T00:00:00+00:00
        2022-01-06T00:00:00+00:00
        2022-01-04T00:00:00+00:00
        2022-01-02T00:00:00+00:00

        >>> # The interval is negative, but the end datetime is after the start datetime.
        >>> # This leads to a generator with no items.
        >>> dt_range = DateTimeRange(
        ...  start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  end_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...  interval=timedelta(days=-2)
        ... )
        >>> list(dt_range)
        []

        >>> # The interval is positive, but the end datetime is before the start datetime.
        >>> # This leads to a generator with no items.
        >>> dt_range = DateTimeRange(
        ...  start_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...  end_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  interval=timedelta(days=2)
        ... )
        >>> list(dt_range)
        []

        >>> # The start and the end datetime are the same.
        >>> # This leads to a generator with no items.
        >>> dt_range = DateTimeRange(
        ...  start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  end_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  interval=timedelta(days=2)
        ... )
        >>> list(dt_range)
        []

    .. _range(): https://docs.python.org/3/library/functions.html#func-range
    """

    interval: TimeInterval
    """The interval between two consecutive datetime instances. It can be both positive and negative."""

    def __iter__(self) -> Generator[datetime, None, None]:
        """Return datetime instances which are within the given period and are equally spaced by the given interval.

        This iterable has a similar behaviour to the Python built-in `range()`_, except that it returns ``datetime``
        instances. Moreover, the built-in ``range()`` has a default value of ``step=1``. However, this iterable does
        not have a default value for ``interval``, i.e. it has to be explicitly provided.

        Note:
            ``end_datetime`` in the period is exclusive, to mimic the behaviour of the built-in `range()`_.

        Yields:
            A generator of datetime instances.
        """
        start = deepcopy(self.start_datetime)
        end = deepcopy(self.end_datetime)
        step = deepcopy(self.interval)

        if start == end:
            return None

        # `negative_interval` is a boolean flag that we use alongside the comparison operator `<`.
        # In particular, we XOR `negative_interval` and the result of `<`.
        # This helps us to know when we should stop in both cases of a positive and a negative interval.
        # We have a single comparison expression which covers both cases.
        negative_interval = step.total_seconds() < 0

        while negative_interval ^ ((next_end := start + step) < end):
            yield start
            start = next_end

        if negative_interval ^ (start < end):
            yield start
