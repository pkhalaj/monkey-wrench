from datetime import UTC, datetime

import pytest

from monkey_wrench.date_time import (
    assert_datetime_has_past,
    assert_datetime_is_timezone_aware,
    assert_start_precedes_end,
    floor_datetime_minutes_to_specific_snapshots,
    number_of_days_in_month,
)

from .const import end_datetime, start_datetime

# ======================================================
### Tests for assert_datetime_is_timezone_aware()

def test_assert_datetime_is_timezone_aware():
    assert_datetime_is_timezone_aware(start_datetime)


def test_assert_datetime_is_timezone_aware_raise():
    dt = datetime(2000, 1, 1, 0, 0, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        assert_datetime_is_timezone_aware(dt)

    assert assert_datetime_is_timezone_aware(dt, silent=True) is False


# ======================================================
### Tests for assert_datetime_has_past()

def test_assert_datetime_has_past():
    assert_datetime_has_past(start_datetime)


def test_assert_datetime_has_past_raise():
    dt = datetime(2100, 1, 1)
    with pytest.raises(ValueError, match="future"):
        assert_datetime_has_past(dt.astimezone(UTC))

    assert assert_datetime_has_past(dt.astimezone(UTC), silent=True) is False

    with pytest.raises(ValueError, match="timezone-aware"):
        assert_datetime_has_past(dt)


# ======================================================
### Tests for assert_start_precedes_end()

def test_assert_start_precedes_end():
    assert_start_precedes_end(start_datetime, end_datetime)


def test_assert_start_precedes_end_raise():
    with pytest.raises(ValueError, match="is later than"):
        assert_start_precedes_end(end_datetime, start_datetime)

    assert assert_start_precedes_end(end_datetime, start_datetime, silent=True) is False

    with pytest.raises(TypeError, match="compare"):
        assert_start_precedes_end(datetime(2000, 1, 1, 0, 0, 0), end_datetime)


# ======================================================
### Tests for days_in_a_month()

@pytest.mark.parametrize(("year", "month", "number_of_days"), [
    (2012, 2, 29),
    (2011, 2, 28),
    (2021, 3, 31),
    (2020, 4, 30),
    (2019, 9, 30)
])
def test_days_in_a_month(year, month, number_of_days):
    assert number_of_days == number_of_days_in_month(year, month)


# ======================================================
### Tests for floor_datetime_minutes()

@pytest.mark.parametrize(("instance", "snapshots", "res"), [
    ([2022, 1, 1, 1, 13], [12, 27, 42, 57], [2022, 1, 1, 1, 12]),
    ([2022, 1, 1, 1, 3], [12, 27, 42, 57], [2022, 1, 1, 0, 57]),
    ([2022, 1, 1, 0, 1], [12, 27, 42, 57], [2021, 12, 31, 23, 57]),
    ([2022, 3, 4, 10, 41], [12, 27, 42, 57], [2022, 3, 4, 10, 27]),
    ([2022, 1, 1, 1, 59], [12, 27, 42, 57], [2022, 1, 1, 1, 57]),
    ([2022, 1, 1, 1, 59], [], [2022, 1, 1, 1, 59]),
    ([2022, 1, 1, 1, 59], None, [2022, 1, 1, 1, 59])
])
def test_floor_datetime_minutes(instance, snapshots, res):
    assert datetime(*res) == floor_datetime_minutes_to_specific_snapshots(datetime(*instance), snapshots)


@pytest.mark.parametrize(("snapshots", "error_message"), [
    ([12, 61], "60"),
    ([1, "a"], "valid integer"),
    ([-1, 12], "greater than"),
    ([1.5, 30], "fractional")
])
def test_floor_datetime_minutes_raise(snapshots, error_message):
    with pytest.raises(ValueError, match=error_message):
        floor_datetime_minutes_to_specific_snapshots(datetime(2022, 1, 1), snapshots)
