from datetime import datetime, timedelta

import pytest

from monkey_wrench.datetime_utils import FilenameParser, datetime_range
from monkey_wrench.query_utils import List
from monkey_wrench.test_utils import (
    get_items_from_shuffled_list_by_original_indices,
    shuffle_list,
)


@pytest.mark.parametrize(("start_datetime", "end_datetime", "reference_indices"), [
    ((2021, 1, 1), (2021, 12, 31), [7]),
    ((2015, 7, 31, 22, 10), (2015, 7, 31, 22, 17), [0, 2, 3, 4, 8]),
    ((2023, 7, 31, 22, 10), (2023, 7, 31, 22, 17), []),
    ((2021, 7, 31, 22, 11), (2021, 7, 31, 22, 11), []),
])
def test_list_query(start_datetime, end_datetime, reference_indices):
    for _ in range(10):
        indices, items = shuffle_list([
            "seviri_20150731_22_16.nc",
            "seviri_20150731_23_13.nc",
            "seviri_20150731_22_14.nc",
            "seviri_20150731_22_15.nc",
            "seviri_20150731_22_12.nc",
            "seviri_20150731_22_19.nc",
            "seviri_20140731_22_10.nc",
            "seviri_20210731_22_11.nc",
            "seviri_20150731_22_16.nc",
        ])

        lq = List(items, FilenameParser)
        expected = get_items_from_shuffled_list_by_original_indices((indices, items), reference_indices)
        assert expected == lq.query(datetime(*start_datetime), datetime(*end_datetime))


@pytest.mark.parametrize(("expected_length", "items"), [
    (2, ["seviri_20150731_22_16.nc", "seviri_20150731_22_17.nc"]),
    (1, ["seviri_20150731_22_16.nc"])
])
def test_list_len(expected_length, items):
    lq = List(items, FilenameParser)
    assert expected_length == lq.len(items)


def test_list_parse_raises():
    with pytest.raises(ValueError, match="a valid datetime object"):
        List(["20150731_22_12", "wrong_format"], FilenameParser)


def test_list_empty_raises():
    with pytest.raises(ValueError, match="List is empty"):
        List([], FilenameParser)


@pytest.mark.parametrize("log_context", [
    "test1",
    "",
])
def test_list_log_context(log_context):
    lq = List(["prefix_20150731_22_12.extension"], FilenameParser, log_context=log_context)
    assert log_context == lq.log_context


def test_list_query_in_batches():
    start_datetime = datetime(2022, 12, 1, 0, 12)
    end_datetime = datetime(2023, 2, 1)

    items = list(datetime_range(start_datetime, end_datetime, timedelta(minutes=15)))[::-1]
    str_items = ["some_prefix_" + i.strftime("%Y%m%d_%H_%M") for i in items]

    lq = List(str_items, FilenameParser)

    next_datetime = end_datetime - timedelta(days=1)
    for batch, count in lq.query_in_batches(start_datetime, end_datetime, timedelta(days=1)):
        day = next_datetime.strftime("%d")
        next_datetime -= timedelta(days=1)
        assert all([day == i[-8:-6] for i in batch])
        assert count in [95, 96]
