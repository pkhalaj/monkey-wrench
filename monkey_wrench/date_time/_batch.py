"""The module providing functions to generate datetime ranges and batches."""

from datetime import datetime, timedelta
from typing import Generator

from pydantic import validate_call


@validate_call
def datetime_range(
        start_datetime: datetime,
        end_datetime: datetime,
        interval: timedelta
) -> Generator[datetime, None, None]:
    """Return datetime instances which are within the given datetime range and are equally spaced by the given interval.

    This function has a similar behaviour to the Python built-in `range()`_, except that it returns
    ``datetime`` instances. Moreover, the built-in ``range()`` has a default value of ``step=1``. However,
    this function does not have a default value for ``interval``, and it has to be explicitly provided.

    Args:
        start_datetime:
            The start of the datetime range (inclusive).
        end_datetime:
            The end of the datetime range (exclusive).
        interval:
            The interval between two consecutive datetime instances. It can be both positive and negative.

    Note:
        The reason that ``end_datetime`` is exclusive, is to mimic the behaviour of the built-in `range()`_.

    Yields:
        A generator of datetime instances.

    Example:
        >>> # Positive interval
        >>> dt_range = datetime_range(
        ...  datetime(2022, 1, 1), datetime(2022, 1, 8), timedelta(days=2)
        ... )
        >>> for datetime_instance in dt_range:
        ...     print(datetime_instance)
        2022-01-01 00:00:00
        2022-01-03 00:00:00
        2022-01-05 00:00:00
        2022-01-07 00:00:00

        >>> # Negative interval
        >>> dt_range = datetime_range(
        ...  datetime(2022, 1, 8), datetime(2022, 1, 1), timedelta(days=-2)
        ... )
        >>> for datetime_instance in dt_range:
        ...     print(datetime_instance)
        2022-01-08 00:00:00
        2022-01-06 00:00:00
        2022-01-04 00:00:00
        2022-01-02 00:00:00

        >>> # The interval is negative, but the end datetime is after the start datetime.
        >>> # This leads to a generator with no items.
        >>> dt_range = datetime_range(
        ...  datetime(2022, 1, 1), datetime(2022, 1, 8), timedelta(days=-2)
        ... )
        >>> list(dt_range)
        []

        >>> # The interval is positive, but the end datetime is before the start datetime.
        >>> # This leads to a generator with no items.
        >>> dt_range = datetime_range(
        ...  datetime(2022, 1, 8), datetime(2022, 1, 1), timedelta(days=2)
        ... )
        >>> list(dt_range)
        []

        >>> # The start and the end datetime are the same.
        >>> # This leads to a generator with no items.
        >>> dt_range = datetime_range(
        ...  datetime(2022, 1, 1), datetime(2022, 1, 1), timedelta(days=2)
        ... )
        >>> list(dt_range)
        []

    .. _range(): https://docs.python.org/3/library/functions.html#func-range
    """
    if start_datetime == end_datetime:
        return None

    # `negative_interval` is a boolean flag that we use alongside the comparison operator `<`.
    # In particular, we XOR `negative_interval` and the result of `<`.
    # This helps us to know when we should stop in both cases of a positive and a negative interval.
    # We have a single comparison expression which covers both cases.
    negative_interval = interval.total_seconds() < 0

    while negative_interval ^ ((next_end_datetime := start_datetime + interval) < end_datetime):
        yield start_datetime
        start_datetime = next_end_datetime

    if negative_interval ^ (start_datetime < end_datetime):
        yield start_datetime


@validate_call
def generate_datetime_batches(
        start_datetime: datetime,
        end_datetime: datetime,
        batch_interval: timedelta
) -> Generator[tuple[datetime, datetime], None, None]:
    """Divide the specified datetime range into smaller batches, i.e. 2-tuples of start and end datetime instances.

    Args:
        start_datetime:
            The start of the datetime range (inclusive).
        end_datetime:
            The end of the datetime range (inclusive).
        batch_interval:
            The datetime interval of a single batch. This is defined as the difference between the two datetime
            instances in each batch. This can be both positive and negative.

    Yields:
        A generator of batches, where each batch is a 2-tuple of the start and end datetime instances. The interval of
        each batch, is equal to ``batch_interval``, except for the last batch if ``end_datetime - start_datetime`` is
        not divisible by ``batch_interval``.

    Warning:
        Note that ``end_datetime`` is inclusive, i.e. it will show up in the last batch. Even if the start and the end
        datetime are equal, we still get one batch. This is different from :func:`datetime_range`, which treats
        ``end_datetime`` as exclusive.

    Warning:
        Depending on the value of ``interval``, the batches can differ. See the examples below.


    Examples:
        >>> # A positive interval, means batches are returned in ascending order.
        >>> # This is with respect to both the start and the end datetime.
        >>> batches = generate_datetime_batches(
        ...  datetime(2022, 1, 1), datetime(2022, 1, 8), timedelta(days=2)
        ... )
        >>> for start, end in batches:
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-01 00:00:00, end=2022-01-03 00:00:00)
        (start=2022-01-03 00:00:00, end=2022-01-05 00:00:00)
        (start=2022-01-05 00:00:00, end=2022-01-07 00:00:00)
        (start=2022-01-07 00:00:00, end=2022-01-08 00:00:00)

        >>> # Compare with the following example, where the interval is negative.
        >>> # The batches are returned in descending order.
        >>> batches = generate_datetime_batches(
        ...   datetime(2022, 1, 8), datetime(2022, 1, 1), timedelta(days=-2)
        ... )
        >>> for start, end in batches:
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-06 00:00:00, end=2022-01-08 00:00:00)
        (start=2022-01-04 00:00:00, end=2022-01-06 00:00:00)
        (start=2022-01-02 00:00:00, end=2022-01-04 00:00:00)
        (start=2022-01-01 00:00:00, end=2022-01-02 00:00:00)

        >>> # The interval is positive, but the end datetime is before the start datetime.
        >>> # This leads to a generator with no items.
        >>> batches = generate_datetime_batches(
        ...   datetime(2022, 1, 8), datetime(2022, 1, 1), timedelta(days=2)
        ... )
        >>> list(batches)
        []

        >>> # The interval is negative, but the end datetime is after the start datetime.
        >>> # This leads to a generator with no items.
        >>> batches = generate_datetime_batches(
        ...   datetime(2022, 1, 1), datetime(2022, 1, 8), timedelta(days=-2)
        ... )
        >>> list(batches)
        []

        >>> # The end datetime is inclusive.
        >>> # Although the start and the end datetime are equal, we still get one batch.
        >>> batches = generate_datetime_batches(
        ...   datetime(2022, 1, 1), datetime(2022, 1, 1), timedelta(days=-2)
        ... )
        >>> for start, end in batches:
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-01 00:00:00, end=2022-01-01 00:00:00)
    """
    if start_datetime == end_datetime:
        yield start_datetime, end_datetime
        return

    # `negative_interval` serves the same purpose as in `datetime_range()`.
    negative_interval = batch_interval.total_seconds() < 0

    if not (negative_interval ^ (end_datetime > start_datetime)):
        return None

    while negative_interval ^ ((next_start_datetime := start_datetime + batch_interval) <= end_datetime):
        yield min(start_datetime, next_start_datetime), max(start_datetime, next_start_datetime)
        start_datetime = next_start_datetime

    # The original datetime range might not necessarily be divisible by `batch_interval`. For example, with `365`
    # days in total, and batches of `30` days, we have `365 % 30 = 5`.
    # Moreover, the `end_datetime` is inclusive.
    # Therefore, we still need the following to fetch the remainder of the datetime range as the final batch.
    yield min(start_datetime, end_datetime), max(start_datetime, end_datetime)
