from collections import Counter

import pytest

from monkey_wrench.datetime_utils import (
    Order,
    datetime_range,
    generate_datetime_batches,
)
from monkey_wrench.test_utils import intervals_equal

from .const import END_DATETIME, INTERVAL, QUOTIENT, REMAINDER, START_DATETIME


@pytest.mark.parametrize(("order", "first_batch", "last_batch"), [
    (Order.decreasing, (END_DATETIME - INTERVAL, END_DATETIME), (START_DATETIME, START_DATETIME + REMAINDER)),
    (Order.increasing, (START_DATETIME, START_DATETIME + INTERVAL), (END_DATETIME - REMAINDER, END_DATETIME))
])
def test_generate_datetime_batches(order, first_batch, last_batch):
    batches = list(generate_datetime_batches(START_DATETIME, END_DATETIME, INTERVAL, order=order))
    assert QUOTIENT + 1 == len(batches)
    assert intervals_equal(INTERVAL, batches[:-1])
    assert Counter(first_batch) == Counter(batches[0])
    assert Counter(last_batch) == Counter(batches[-1])


@pytest.mark.parametrize("order", [
    Order.decreasing,
    Order.increasing,
])
def test_generate_datetime_batches_raise(order):
    with pytest.raises(ValueError, match="is later than"):
        list(generate_datetime_batches(END_DATETIME, START_DATETIME, INTERVAL, order=order))


def test_datetime_range():
    datetime_objects = list(datetime_range(START_DATETIME, END_DATETIME, INTERVAL))

    n = len(datetime_objects)

    assert QUOTIENT + 1 == n
    assert START_DATETIME == datetime_objects[0]
    assert END_DATETIME > datetime_objects[-1]
    assert intervals_equal(INTERVAL, datetime_objects)


def test_datetime_range_empty():
    assert [] == list(datetime_range(END_DATETIME, END_DATETIME, INTERVAL))
