from calendar import monthrange
from datetime import UTC, datetime, timedelta
from typing import assert_never

from pydantic import validate_call

from monkey_wrench.date_time._types import Day, Minutes, Month, Year
from monkey_wrench.generic import assert_


def assert_datetime_is_timezone_aware(datetime_object: datetime, silent: bool = False) -> bool:
    """Assert that the ``datetime_object`` is timezone-aware.

    Note:
        This function relies on :func:`~monkey_wrench.generic.assert_`.

    Examples:
        >>> assert_datetime_is_timezone_aware(datetime.now(), silent=True)
        False

        >>> assert_datetime_is_timezone_aware(datetime.now(UTC))
        True
    """
    try:
        result = None not in [datetime_object.tzinfo, datetime_object.tzinfo.utcoffset(datetime_object)]
    except AttributeError:
        result = False

    return assert_(result, f"{datetime_object} is not timezone-aware!", silent=silent)


@validate_call
def assert_start_precedes_end(start_datetime: datetime, end_datetime: datetime, silent: bool = False) -> bool:
    """Assert that the ``start_datetime`` is not later than the ``end_datetime``.

    Note:
        This function relies on :func:`~monkey_wrench.generic.assert_`.

    Examples:
        >>> # The following will not raise an exception.
        >>> assert_start_precedes_end(datetime(2020, 1, 1), datetime(2020, 12, 31))
        True

        >>> # The following will raise an exception!
        >>> assert_start_precedes_end(datetime(2020, 1, 2), datetime(2020, 1, 1), silent=True)
        False

        >>> # The following will raise an exception!
        >>> # assert_start_precedes_end(datetime(2020, 1, 2), datetime(2020, 1, 1))
    """
    return assert_(
        start_datetime <= end_datetime,
        f"start_datetime='{start_datetime}' is later than end_datetime='{end_datetime}'.",
        silent=silent
    )


def assert_datetime_has_past(datetime_instance: datetime, silent: bool = False) -> bool:
    """Assert that the ``datetime_instance`` is in not in the future.

    Note:
        This function relies on :func:`~monkey_wrench.generic.assert_`.

    Examples:
        >>> # The following will not raise an exception.
        >>> assert_datetime_has_past(datetime(2020, 1, 1, tzinfo=UTC))
        True

        >>> assert_datetime_has_past(datetime(2100, 1, 2, tzinfo=UTC), silent=True)
        False

        >>> # The following will raise an exception!
        >>> # assert_has_datetime_past(datetime(2100, 1, 2, tzinfo=UTC))
    """
    assert_datetime_is_timezone_aware(datetime_instance, silent=False)
    return assert_(
        datetime_instance <= datetime.now(UTC),
        "The given datetime instance is in the future!",
        silent=silent
    )


@validate_call
def number_of_days_in_month(year: Year, month: Month) -> Day:
    """Return the number of days in a month, taking into account both common and leap years.

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

    assert_never(datetime_instance)
