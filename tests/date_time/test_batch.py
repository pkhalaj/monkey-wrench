from collections import Counter

import pytest

from monkey_wrench.date_time import DateTimePeriod, DateTimePeriodStrict, DateTimeRange, DateTimeRangeInBatches
from tests.utils import intervals_equal

from .const import end_datetime, interval, quotient, remainder, start_datetime

# ======================================================
### Tests for DateTimeRangeInBatches()

@pytest.mark.parametrize(("batches", "first_batch", "last_batch"), [
    (
            DateTimeRangeInBatches(start_datetime=start_datetime, end_datetime=end_datetime, batch_interval=interval),
            DateTimePeriod(start_datetime=start_datetime, end_datetime=start_datetime + interval),
            DateTimePeriod(start_datetime=end_datetime - remainder, end_datetime=end_datetime)
    ),
    (
            DateTimeRangeInBatches(start_datetime=end_datetime, end_datetime=start_datetime, batch_interval=-interval),
            DateTimePeriod(start_datetime=end_datetime - interval, end_datetime=end_datetime),
            DateTimePeriod(start_datetime=start_datetime, end_datetime=start_datetime + remainder)
    )

])
def test_DateTimeRangeInBatches(batches, first_batch, last_batch):
    batches_list = list(batches)
    assert quotient + 1 == len(batches_list)
    assert intervals_equal(interval, batches_list[:-1])
    assert Counter(first_batch) == Counter(batches_list[0])
    assert Counter(last_batch) == Counter(batches_list[-1])
    assert batches.datetime_range_in_batches == batches
    assert list(batches.datetime_range_in_batches) == batches_list


@pytest.mark.parametrize(("start_datetime", "end_datetime", "temporal_sign", "result"), [
    (start_datetime, end_datetime, -1, []),
    (end_datetime, start_datetime, +1, []),

    (end_datetime, end_datetime, -1, [DateTimePeriodStrict(start_datetime=end_datetime, end_datetime=end_datetime)]),
    (start_datetime, start_datetime, +1,
     [DateTimePeriodStrict(start_datetime=start_datetime, end_datetime=start_datetime)])
])
def test_DateTimeRangeInBatches_empty_or_single(start_datetime, end_datetime, temporal_sign, result):
    assert result == list(
        DateTimeRangeInBatches(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            batch_interval=temporal_sign * interval
        )
    )


# ======================================================
### Tests for DateTimeRange()

@pytest.mark.parametrize(("start_datetime", "end_datetime", "temporal_sign"), [
    (start_datetime, end_datetime, 1),
    (end_datetime, start_datetime, -1)
])
def test_DateTimeRange(start_datetime, end_datetime, temporal_sign):
    datetime_objects = list(
        DateTimeRange(start_datetime=start_datetime, end_datetime=end_datetime, interval=temporal_sign * interval)
    )
    assert len(datetime_objects) == quotient + 1
    assert start_datetime == datetime_objects[0]
    assert temporal_sign ^ (end_datetime < datetime_objects[-1])
    assert intervals_equal(temporal_sign * interval, datetime_objects)


@pytest.mark.parametrize(("start_datetime", "end_datetime", "temporal_sign"), [
    (start_datetime, end_datetime, -1),
    (end_datetime, start_datetime, +1),
    (start_datetime, start_datetime, -1),
    (start_datetime, start_datetime, +1),
])
def test_DateTimeRange_empty(start_datetime, end_datetime, temporal_sign):
    assert [] == list(
        DateTimeRange(start_datetime=start_datetime, end_datetime=end_datetime, interval=temporal_sign * interval)
    )
