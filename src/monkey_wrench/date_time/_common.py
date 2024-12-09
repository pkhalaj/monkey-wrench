"""The module which defines common functionalities needed in the :obj:`date_time` package."""

from calendar import monthrange
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Never

from pydantic import Field, NonNegativeInt, PositiveInt, validate_call

Minutes = Annotated[NonNegativeInt, Field(lt=60)]
"""Type alias for minutes."""


class Order(Enum):
    """An enum to determine the order of sorting."""
    increasing = 1
    decreasing = 2


@validate_call
def assert_start_time_is_before_end_time(start_datetime: datetime, end_datetime: datetime) -> None | Never:
    """Raise a ``ValueError`` If ``start_datetime`` is later than the ``end_datetime``.

    Warning:
        Do not use an ``assert`` keyword in combination with this function. The assertion is implicitly done in the
        function.
    """
    if start_datetime > end_datetime:
        raise ValueError(f"start_datetime='{start_datetime}' is later than end_datetime='{end_datetime}'.")


@validate_call
def number_of_days_in_month(year: PositiveInt, month: PositiveInt) -> int:
    """Return the number of days in a month, taking into account the leap years.

    Args:
        year:
            The year as a 4 digit positive integer.
        month:
            The month number, e.g. ``1`` corresponds to ``January``.

    Returns:
        The number of days in a month.

    Example:
        >>> from monkey_wrench.date_time import number_of_days_in_month
        >>> number_of_days_in_month(2018, 2) # a common year
        28
        >>> number_of_days_in_month(2020, 2) # a leap year
        29
    """
    return monthrange(year, month)[1]


@validate_call
def floor_datetime_minutes_to_snapshots(snapshots: list[Minutes], datetime_instance: datetime) -> datetime:
    """Round down or floor the given datetime to the closest minute from the snapshots.

    Args:
        snapshots:
            A sorted list of minutes. As an example, for SEVIRI we have one snapshot per ``15`` minutes, starting
            from the 12th minute. As a result, we have ``[12, 27, 42, 57]`` for SEVIRI snapshots in an hour.
        datetime_instance:
            The datetime instance to floor.

    Returns:
        A datetime instance which is smaller than or equal to ``datetime_instance``, such that the minute matches the
        closest minute from the ``snapshots``.

    Example:
          >>> from datetime import datetime
          >>> from monkey_wrench.date_time import floor_datetime_minutes_to_snapshots
          >>> seviri_snapshots = [12, 27, 42, 57]
          >>> floor_datetime_minutes_to_snapshots(seviri_snapshots, datetime(2020, 1, 1, 0, 3))
          datetime.datetime(2019, 12, 31, 23, 57)
          >>> floor_datetime_minutes_to_snapshots(seviri_snapshots, datetime(2020, 1, 1, 0, 58))
          datetime.datetime(2020, 1, 1, 0, 57)
          >>> floor_datetime_minutes_to_snapshots(seviri_snapshots, datetime(2020, 1, 1, 1, 30))
          datetime.datetime(2020, 1, 1, 1, 27)
    """
    if not snapshots:
        return datetime_instance

    snapshots = sorted(snapshots)
    minute = datetime_instance.minute
    _datetime_base = datetime(datetime_instance.year, datetime_instance.month, datetime_instance.day,
                              datetime_instance.hour)
    if minute < snapshots[0]:
        return _datetime_base - timedelta(minutes=60 - snapshots[-1])

    snapshots += [60]
    for i in range(len(snapshots) - 1):
        if snapshots[i] <= minute < snapshots[i + 1]:
            return _datetime_base + timedelta(minutes=snapshots[i])
