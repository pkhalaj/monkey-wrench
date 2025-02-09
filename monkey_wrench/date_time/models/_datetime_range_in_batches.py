"""The module providing the ``DateTimeRangeInBatches`` model."""

from typing import Generator

from monkey_wrench.date_time.models._base import DateTimePeriod, TimeInterval


class DateTimeRangeInBatches(DateTimePeriod):
    """Pydantic model to for a datetime range in batches.

    Note:
        This can be used both as a model and also as a generator. See the examples below.

    Warning:
        Note that ``end_datetime`` is inclusive, i.e. it will show up in the last batch. Even if the start and the end
        datetime are equal, we still get one batch. This is different from :class:`DateTimeRange`, which treats
        ``end_datetime`` as exclusive.

    Warning:
        Depending on the value of ``batch_interval``, the batches can differ. See the examples below.

    Examples:
        >>> from datetime import UTC, datetime, timedelta
        >>>
        >>> # A positive interval, means batches are returned in ascending order.
        >>> # This is with respect to both the start and the end datetime.
        >>> batches = DateTimeRangeInBatches(
        ...  start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...  end_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...  batch_interval=timedelta(days=2)
        ... )
        >>> for batch in batches:
        ...     start = batch.start_datetime.isoformat()
        ...     end = batch.end_datetime.isoformat()
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-01T00:00:00+00:00, end=2022-01-03T00:00:00+00:00)
        (start=2022-01-03T00:00:00+00:00, end=2022-01-05T00:00:00+00:00)
        (start=2022-01-05T00:00:00+00:00, end=2022-01-07T00:00:00+00:00)
        (start=2022-01-07T00:00:00+00:00, end=2022-01-08T00:00:00+00:00)

        >>> # Compare with the following example, where the interval is negative.
        >>> # The batches are returned in descending order.
        >>> batches = DateTimeRangeInBatches(
        ...   start_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...   end_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...   batch_interval=timedelta(days=-2)
        ... )
        >>> for batch in batches:
        ...     start = batch.start_datetime.isoformat()
        ...     end = batch.end_datetime.isoformat()
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-06T00:00:00+00:00, end=2022-01-08T00:00:00+00:00)
        (start=2022-01-04T00:00:00+00:00, end=2022-01-06T00:00:00+00:00)
        (start=2022-01-02T00:00:00+00:00, end=2022-01-04T00:00:00+00:00)
        (start=2022-01-01T00:00:00+00:00, end=2022-01-02T00:00:00+00:00)

        >>> # The interval is positive, but the end datetime is before the start datetime.
        >>> # This leads to a generator with no items.
        >>> batches = DateTimeRangeInBatches(
        ...   start_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...   end_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...   batch_interval=timedelta(days=2)
        ... )
        >>> list(batches)
        []

        >>> # The interval is negative, but the end datetime is after the start datetime.
        >>> # This leads to a generator with no items.
        >>> batches = DateTimeRangeInBatches(
        ...   start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...   end_datetime=datetime(2022, 1, 8, tzinfo=UTC),
        ...   batch_interval=timedelta(days=-2)
        ... )
        >>> list(batches)
        []

        >>> # The end datetime is inclusive.
        >>> # Although the start and the end datetime are equal, we still get one batch.
        >>> batches = DateTimeRangeInBatches(
        ...   start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...   end_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        ...   batch_interval=timedelta(days=-2)
        ... )
        >>> for batch in batches:
        ...     start = batch.start_datetime.isoformat()
        ...     end = batch.end_datetime.isoformat()
        ...     print(f"(start={start}, end={end})")
        (start=2022-01-01T00:00:00+00:00, end=2022-01-01T00:00:00+00:00)
    """
    batch_interval: TimeInterval
    """The datetime interval of a single batch. It can be both positive and negative.

    This is defined as the difference between the two datetime instances in each batch.

    Note:
        As a rule of thumb this paramerer can be set to ``30`` days. A smaller value for ``batch_interval``
        means a larger number of batches which increases the overall time needed to fetch all the products.
        A larger value for ``batch_interval`` shortens the total time to fetch all the products, however, you might
        get an error regarding sending `too many requests` to the server.

    Note:
        The interval of each batch, is equal to ``batch_interval``, except for the last batch if
        ``end_datetime - start_datetime`` is not divisible by ``batch_interval``.
    """

    def __iter__(self) -> Generator[DateTimePeriod, None, None]:
        """Divide the specified datetime range into smaller batches, i.e. 2-tuples of start and end datetime instances.

        Yields:
            A generator of batches, where each batch is a 2-tuple of the start and end datetime instances.
        """
        start = self.start_datetime
        end = self.end_datetime
        _batch_interval = self.batch_interval

        if start == end:
            yield DateTimePeriod(start_datetime=start, end_datetime=end)
            return

        # `negative_interval` serves the same purpose as in `datetime_range()`.
        negative_interval = _batch_interval.total_seconds() < 0

        if not (negative_interval ^ (end > start)):
            return None

        while negative_interval ^ ((next_start := start + _batch_interval) <= end):
            yield DateTimePeriod(start_datetime=min(start, next_start), end_datetime=max(start, next_start))
            start = next_start

        # The original datetime range might not necessarily be divisible by `batch_interval`. For example, with `365`
        # days in total, and batches of `30` days, we have `365 % 30 = 5`.
        # Moreover, the `end_datetime` is inclusive.
        # Therefore, we still need the following to fetch the remainder of the datetime range as the final batch.
        if start != end:
            yield DateTimePeriod(start_datetime=min(start, end), end_datetime=max(start, end))
