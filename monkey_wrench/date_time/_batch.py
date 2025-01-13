"""The module providing functions to generate datetime ranges and batches."""

from datetime import datetime, timedelta
from typing import Generator

from pydantic import validate_call

from monkey_wrench.date_time._common import assert_start_time_is_before_end_time
from monkey_wrench.generic import Order


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
            The end of the datetime range (exclusive), i.e. it will be strictly larger than the last returned
            datetime instance.
        interval:
            The interval between two consecutive datetime instances.

    Note:
        The reason that ``end_datetime`` is exclusive, is to mimic the behaviour of the built-in `range()`_.

    Yields:
        A generator of datetime instances.

    Example:
        >>> dt_range = datetime_range(
        ...  datetime(2022, 1, 1), datetime(2022, 1, 8), timedelta(days=2)
        ... )
        >>> for datetime_instance in dt_range:
        ...     print(datetime_instance)
        2022-01-01 00:00:00
        2022-01-03 00:00:00
        2022-01-05 00:00:00
        2022-01-07 00:00:00

    .. _range(): https://docs.python.org/3/library/functions.html#func-range
    """
    while (next_end_datetime := start_datetime + interval) < end_datetime:
        yield start_datetime
        start_datetime = next_end_datetime

    if start_datetime < end_datetime:
        yield start_datetime


@validate_call
def generate_datetime_batches(
        start_datetime: datetime,
        end_datetime: datetime,
        batch_interval: timedelta,
        order: Order = Order.descending
) -> Generator[tuple[datetime, datetime], None, None]:
    """Divide the specified datetime range into smaller batches, i.e. 2-tuples of start and end datetime instances.

    Args:
        start_datetime:
            The start of the datetime range (inclusive).
        end_datetime:
            The end of the datetime range (inclusive).
        batch_interval:
            The datetime interval of a single batch. This is defined as the difference between the two datetime
            instances in each batch.
        order:
            Either :obj:`~monkey_wrench.generic.Order.ascending` or :obj:`~monkey_wrench.generic.Order.descending`.
            Defaults to :obj:`~monkey_wrench.generic.Order.descending`.

    Yields:
        A generator of batches, where each batch is a 2-tuple of the start and end datetime instances. The interval of
        each batch, is equal to ``batch_interval``, except for the last batch if ``end_datetime - start_datetime`` is
        not divisible by ``batch_interval``.

    Warning:
        Note that ``end_datetime`` is inclusive, i.e. it will show up in the last batch. This is different from
        :func:`datetime_range`, which treats ``end_datetime`` as exclusive.

    Warning:
        Depending on the value of ``order``, the batches can differ. See the examples below.

    Raises:
        ValueError:
            Refer to :func:`~monkey_wrench.date_time.assert_start_time_is_before_end_time`.

    Examples:
        >>> # By default, batches are returned in descending order,
        >>> # with respect to both the start and the end datetime.
        >>> batches = generate_datetime_batches(
        ...  datetime(2022, 1, 1), datetime(2022, 1, 8), timedelta(days=2)
        ... )
        >>> for start, end in batches:
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-06 00:00:00, end=2022-01-08 00:00:00)
        (start=2022-01-04 00:00:00, end=2022-01-06 00:00:00)
        (start=2022-01-02 00:00:00, end=2022-01-04 00:00:00)
        (start=2022-01-01 00:00:00, end=2022-01-02 00:00:00)

        >>> # Compare with the following example,
        >>> # in which the batches are returned in ascending order.
        >>> batches = generate_datetime_batches(
        ...   datetime(2022, 1, 1), datetime(2022, 1, 8), timedelta(days=2), order=Order.ascending
        ... )
        >>> for start, end in batches:
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-01 00:00:00, end=2022-01-03 00:00:00)
        (start=2022-01-03 00:00:00, end=2022-01-05 00:00:00)
        (start=2022-01-05 00:00:00, end=2022-01-07 00:00:00)
        (start=2022-01-07 00:00:00, end=2022-01-08 00:00:00)
    """
    assert_start_time_is_before_end_time(start_datetime, end_datetime)

    match order:
        case Order.descending:
            while (next_start_datetime := end_datetime - batch_interval) >= start_datetime:
                yield next_start_datetime, end_datetime
                end_datetime = next_start_datetime
        case Order.ascending:
            while (next_end_datetime := start_datetime + batch_interval) < end_datetime:
                yield start_datetime, next_end_datetime
                start_datetime = next_end_datetime

    # The original datetime range might not necessarily be divisible by `batch_interval`. For example, with `365`
    # days in total, and batches of `30` days, we have `365 % 30 = 5`.
    # Therefore, we need the following to fetch the remainder of the datetime range as the final batch.
    if start_datetime < end_datetime:
        yield start_datetime, end_datetime
