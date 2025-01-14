from collections import Counter

import pytest

from monkey_wrench.date_time import (
    datetime_range,
    generate_datetime_batches,
)
from tests.utils import intervals_equal

from .const import end_datetime, interval, quotient, remainder, start_datetime

# ======================================================
### Tests for generate_datetime_batches()

@pytest.mark.parametrize(("batches", "first_batch", "last_batch"), [
    (
            generate_datetime_batches(start_datetime, end_datetime, interval),
            (start_datetime, start_datetime + interval),
            (end_datetime - remainder, end_datetime)
    ),
    (
            generate_datetime_batches(end_datetime, start_datetime, -interval),
            (end_datetime - interval, end_datetime),
            (start_datetime, start_datetime + remainder)
    )

])
def test_generate_datetime_batches(batches, first_batch, last_batch):
    batches = list(batches)
    assert quotient + 1 == len(batches)
    assert intervals_equal(interval, batches[:-1])
    assert Counter(first_batch) == Counter(batches[0])
    assert Counter(last_batch) == Counter(batches[-1])


@pytest.mark.parametrize(("start_datetime", "end_datetime", "temporal_sign", "result"), [
    (start_datetime, end_datetime, -1, []),
    (end_datetime, start_datetime, +1, []),

    (end_datetime, end_datetime, -1, [(end_datetime, end_datetime)]),
    (start_datetime, start_datetime, +1, [(start_datetime, start_datetime)]),
])
def test_generate_datetime_batches_empty_or_single(start_datetime, end_datetime, temporal_sign, result):
    assert result == list(generate_datetime_batches(start_datetime, end_datetime, temporal_sign * interval))


# ======================================================
### Tests for datetime_range()

@pytest.mark.parametrize(("start_datetime", "end_datetime", "temporal_sign"), [
    (start_datetime, end_datetime, 1),
    (end_datetime, start_datetime, -1)
])
def test_datetime_range(start_datetime, end_datetime, temporal_sign):
    datetime_objects = list(datetime_range(start_datetime, end_datetime, temporal_sign * interval))
    assert quotient + 1 == len(datetime_objects)
    assert start_datetime == datetime_objects[0]
    assert temporal_sign ^ (end_datetime < datetime_objects[-1])
    assert intervals_equal(temporal_sign * interval, datetime_objects)


@pytest.mark.parametrize(("start_datetime", "end_datetime", "temporal_sign"), [
    (start_datetime, end_datetime, -1),
    (end_datetime, start_datetime, +1),

])
def test_datetime_range_empty(start_datetime, end_datetime, temporal_sign):
    assert [] == list(datetime_range(start_datetime, end_datetime, temporal_sign * interval))
