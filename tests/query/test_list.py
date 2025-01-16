from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from monkey_wrench.date_time import FilePathParser, datetime_range
from monkey_wrench.input_output.seviri import input_filename_from_datetime
from monkey_wrench.query import List
from tests.utils import (
    get_items_from_shuffled_list_by_original_indices,
    randomly_remove_from_list,
    shuffle_list,
)

start_datetime = datetime(2022, 1, 1, 0, 12)
end_datetime = datetime(2022, 1, 1, 5, 27)
interval = timedelta(minutes=15)

elements = [input_filename_from_datetime(i) for i in datetime_range(start_datetime, end_datetime, interval)]


# ======================================================
### Tests for List.query()

@pytest.mark.parametrize(("start_datetime", "end_datetime", "reference_indices"), [
    ((2021, 1, 1), (2021, 12, 31), [7]),
    ((2015, 7, 31, 22, 10), (2015, 7, 31, 22, 17), [0, 2, 3, 4, 8]),
    ((2023, 7, 31, 22, 10), (2023, 7, 31, 22, 17), []),
    ((2021, 7, 31, 22, 11), (2021, 7, 31, 22, 11), []),
])
def test_List_query(start_datetime, end_datetime, reference_indices):
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
        lq = List(items, FilePathParser)
        expected = get_items_from_shuffled_list_by_original_indices((indices, items), reference_indices)

        assert expected == lq.query(datetime(*start_datetime), datetime(*end_datetime))
        assert expected == [items[i] for i in lq.query_indices(datetime(*start_datetime), datetime(*end_datetime))]
        assert expected == lq[lq.query_indices(datetime(*start_datetime), datetime(*end_datetime))]


# ======================================================
### Tests for List()

def test_List_parse_raise():
    with pytest.raises(ValueError, match="a valid datetime object"):
        List(["20150731_22_12", "wrong_format"], FilePathParser)


def test_List_empty_raise():
    with pytest.raises(ValueError, match="List is empty"):
        List([], FilePathParser)


@pytest.mark.parametrize("log_context", ["test1", ""])
def test_list_log_context(log_context):
    lq = List(["prefix_20150731_22_12.extension"], FilePathParser, log_context=log_context)
    assert log_context == lq.log_context


# ======================================================
### Tests for List.to_python_list()

@pytest.mark.parametrize(("expected_length", "items"), [
    (2, ["seviri_20150731_22_16.nc", "seviri_20150731_22_17.nc"]),
    (1, ["seviri_20150731_22_16.nc"])
])
def test_list_as_list(expected_length, items):
    lq = List(items, FilePathParser)
    assert items == lq
    assert items == lq.to_python_list()
    assert isinstance(lq.to_python_list(), list)
    assert isinstance(lq.to_python_list()[0], str)
    assert expected_length == List.len(lq)


# ======================================================
### Tests for List.query_in_batches()

def test_list_query_in_batches():
    items = list(datetime_range(start_datetime, end_datetime, timedelta(minutes=5)))
    str_items = ["some_prefix_" + i.strftime("%Y%m%d_%H_%M") for i in items]
    lq = List(str_items[::-1], FilePathParser)

    index = 0
    for batch, _ in lq.query_in_batches(start_datetime, end_datetime, timedelta(hours=1)):
        assert set(str_items[index: index + 12]) == set(batch)
        index += 12


# ======================================================
### Tests for List.normalize_index()

@pytest.mark.parametrize(("index", "res"), [
    (0, 0),
    (-1, 20),
    (-21, 0),
    (-5, 16),
    (20, 20),
    (12, 12),
])
def test_normalize_index(index, res):
    lst = List(elements, FilePathParser)
    assert res == lst.normalize_index(index)


@pytest.mark.parametrize("index", [
    21,
    -22,
    -49,
    22,
])
def test_normalize_index_raise(index):
    with pytest.raises(IndexError, match="out of range"):
        List(elements, FilePathParser).normalize_index(index)


# ======================================================
### Tests for List.k_sized_batches()

@pytest.mark.parametrize(("k", "idx_start", "idx_end", "err", "msg"), [
    (-1, 0, 10, ValidationError, "greater than 0"),
    (30, 0, 10, ValueError, "batch size"),
    (10, 15, 10, ValueError, "cannot be greater"),
])
def test_k_sized_batches_raise(k, idx_start, idx_end, err, msg):
    with pytest.raises(err, match=msg):
        list(List(elements, FilePathParser).generate_k_sized_batches_by_index(k, idx_start, idx_end))


@pytest.mark.parametrize(("k", "idx_start", "idx_end"), [
    (16, 0, -1),
    (13, 12, 15),
    (5, 10, 18),
    (16, 10, 14),
    (19, 18, 18)
])
def test_k_sized_batches(k, idx_start, idx_end):
    _, available, removed = randomly_remove_from_list(elements, 2)
    lst = List(sorted(list(available)), FilePathParser)

    batches = list(lst.generate_k_sized_batches_by_index(k, idx_start, idx_end))
    idx_start = lst.normalize_index(idx_start)
    idx_end = lst.normalize_index(idx_end)

    if idx_start < k:
        idx_start = k - 1
    if idx_end < k:
        idx_end = k - 1
    assert (idx_end - idx_start) + 1 == len(batches)

    prev_batch = batches[0]
    for batch in batches[1:-1]:
        assert k == len(set(batch))
        assert sorted(batch) == batch
        assert batch[-1] > batch[0]
        assert prev_batch[-1] < batch[-1]
        assert prev_batch[0] < batch[0]
        assert [*prev_batch[1:], batch[-1]] == batch
        prev_batch = batch
