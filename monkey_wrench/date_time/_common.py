"""The module providing common functionalities for the ``date_time`` package."""

from calendar import monthrange
from datetime import datetime, timedelta
from typing import Never

from pydantic import PositiveInt, validate_call

from monkey_wrench.date_time._types import Minutes


@validate_call
def assert_start_precedes_end(start_datetime: datetime, end_datetime: datetime) -> None | Never:
    """Raise a ``ValueError`` if ``start_datetime`` is later than the ``end_datetime``, otherwise return ``None``.

    Warning:
        Do not use ``assert`` in combination with this function. The assertion is implicitly done in the
        function.

    Raises:
        ValueError:
            If ``start_datetime`` is later than the ``end_datetime``.

    Examples:
        >>> # The following will not raise an exception.
        >>> assert_start_precedes_end(datetime(2020, 1, 1), datetime(2020, 12, 31))

        >>> # The following will raise an exception!
        >>> # assert_start_precedes_end(datetime(2020, 1, 2), datetime(2020, 1, 1))
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
            The one-based numbering of the given month, e.g. ``1`` corresponds to `January`.

    Returns:
        The number of days in a month.

    Examples:
        >>> # `2018` was a common year.
        >>> number_of_days_in_month(2018, 2)
        28

        >>> # `2020` was a leap year.
        >>> number_of_days_in_month(2020, 2)
        29
    """
    return monthrange(year, month)[1]


@validate_call
def floor_datetime_minutes_to_specific_snapshots(
        datetime_instance: datetime, snapshots: Minutes | None = None
) -> datetime:
    """Floor the given datetime instance to the closest minute from the given list of snapshots.

    Args:
        datetime_instance:
            The datetime instance to floor.
        snapshots:
            A (sorted) list of minutes. Defaults to ``None``, which means the given datetime instance will be returned
            as it is, without any modifications. As an example, for SEVIRI we have one snapshot per ``15`` minutes,
            starting from the 12th minute. As a result, we have ``[12, 27, 42, 57]`` for SEVIRI snapshots in an hour.
            The ``snapshots`` will be first sorted in increasing order.

    Returns:
        A datetime instance which is smaller than or equal to the given ``datetime_instance``, such that the minute
        matches the closest minute from the ``snapshots``.

    Examples:
          >>> floor_datetime_minutes_to_specific_snapshots(
          ...  datetime(2020, 1, 1, 0, 3), [12, 27, 42, 57]
          ... )
          datetime.datetime(2019, 12, 31, 23, 57)

          >>> floor_datetime_minutes_to_specific_snapshots(
          ...  datetime(2020, 1, 1, 0, 58), [12, 27, 42, 57]
          ... )
          datetime.datetime(2020, 1, 1, 0, 57)

          >>> floor_datetime_minutes_to_specific_snapshots(
          ...  datetime(2020, 1, 1, 1, 30), [12, 27, 42, 57]
          ... )
          datetime.datetime(2020, 1, 1, 1, 27)

          >>> floor_datetime_minutes_to_specific_snapshots(
          ...  datetime(2020, 1, 1, 1, 27), [12, 27, 42, 57]
          ... )
          datetime.datetime(2020, 1, 1, 1, 27)

          >>> floor_datetime_minutes_to_specific_snapshots(
          ...  datetime(2020, 1, 1, 1, 26)
          ... )
          datetime.datetime(2020, 1, 1, 1, 26)
    """
    if not snapshots:
        return datetime_instance

    snapshots = sorted(snapshots, reverse=False)
    minute = datetime_instance.minute
    _datetime_base = datetime(
        datetime_instance.year, datetime_instance.month, datetime_instance.day, datetime_instance.hour
    )

    if minute < snapshots[0]:
        return _datetime_base - timedelta(minutes=60 - snapshots[-1])

    snapshots += [60]
    for i in range(len(snapshots) - 1):
        if snapshots[i] <= minute < snapshots[i + 1]:
            return _datetime_base + timedelta(minutes=snapshots[i])
