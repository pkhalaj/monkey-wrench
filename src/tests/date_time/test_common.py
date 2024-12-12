from datetime import datetime

import pytest

from monkey_wrench.date_time import (
    assert_start_time_is_before_end_time,
    floor_datetime_minutes_to_snapshots,
    number_of_days_in_month,
)

from .const import END_DATETIME, START_DATETIME


@pytest.mark.parametrize(("start_datetime", "end_datetime", "error_message"), [
    (START_DATETIME, END_DATETIME, None),
    (END_DATETIME, START_DATETIME, "is later than"),
])
def test_assert_start_time_before_end_time(start_datetime, end_datetime, error_message):
    if error_message is None:
        assert_start_time_is_before_end_time(start_datetime, end_datetime)
    else:
        with pytest.raises(ValueError, match=error_message):
            assert_start_time_is_before_end_time(start_datetime, end_datetime)


@pytest.mark.parametrize(("year", "month", "number_of_days"), [
    (2012, 2, 29),
    (2011, 2, 28),
    (2021, 3, 31),
    (2020, 4, 30),
    (2019, 9, 30)
])
def test_days_in_a_month(year, month, number_of_days):
    assert number_of_days == number_of_days_in_month(year, month)


@pytest.mark.parametrize(("instance", "snapshots", "res"), [
    ([2022, 1, 1, 1, 13], [12, 27, 42, 57], [2022, 1, 1, 1, 12]),
    ([2022, 1, 1, 1, 3], [12, 27, 42, 57], [2022, 1, 1, 0, 57]),
    ([2022, 1, 1, 0, 1], [12, 27, 42, 57], [2021, 12, 31, 23, 57]),
    ([2022, 3, 4, 10, 41], [12, 27, 42, 57], [2022, 3, 4, 10, 27]),
    ([2022, 1, 1, 1, 59], [12, 27, 42, 57], [2022, 1, 1, 1, 57]),
    ([2022, 1, 1, 1, 59], [], [2022, 1, 1, 1, 59])
])
def test_floor_datetime_minutes(instance, snapshots, res):
    assert datetime(*res) == floor_datetime_minutes_to_snapshots(snapshots, datetime(*instance))


@pytest.mark.parametrize(("snapshots", "error_message"), [
    ([12, 61], "60"),
    ([1, "a"], "valid integer"),
    ([-1, 12], "greater than"),
    ([1.5, 30], "fractional")
])
def test_floor_datetime_minutes_raise(snapshots, error_message):
    with pytest.raises(ValueError, match=error_message):
        floor_datetime_minutes_to_snapshots(snapshots, datetime(2022, 1, 1))
