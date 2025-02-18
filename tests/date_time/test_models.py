import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from monkey_wrench.date_time import AwarePastDateTime, DateTimePeriod, TimeDeltaDict, TimeInterval
from monkey_wrench.generic import Model

from .const import end_datetime, start_datetime

# ======================================================
### Tests for TimeDeltaDict()

@pytest.mark.parametrize("interval", [
    dict(weeks=10, seconds=2),
    dict(days=20, hours=2),
])
def test_TimeDeltaDict(interval):
    class Test(Model):
        interval: TimeDeltaDict

    assert Test(interval=interval).interval == datetime.timedelta(**interval)


@pytest.mark.parametrize("interval", [
    dict(),
    dict(days=20, hours=2, weeks=10, minutes=2, seconds=2, milliseconds=2),
])
def test_TimeDeltaDict_raise(interval):
    class Test(Model):
        interval: TimeDeltaDict

    with pytest.raises(ValidationError, match="valid"):
        assert Test(interval=interval)


# ======================================================
### Tests for TimeInterval()

@pytest.mark.parametrize("interval", [
    dict(weeks=10, seconds=2),
    datetime.timedelta(weeks=10, seconds=2),
])
def test_TimeInterval(interval):
    class Test(Model):
        interval: TimeInterval

    assert Test(interval=interval).interval == datetime.timedelta(weeks=10, seconds=2)


# ======================================================
### Tests for AwarePastDateTime()

@pytest.mark.parametrize("dt", [
    "2000-01-01T00:00:00+01:00",
    datetime.datetime(2000, 1, 1, tzinfo=ZoneInfo("Europe/Stockholm")),
])
def test_AwarePastDateTime(dt):
    class Test(Model):
        dt: AwarePastDateTime

    assert Test(dt=dt).dt == datetime.datetime(2000, 1, 1, tzinfo=ZoneInfo("Europe/Stockholm"))


@pytest.mark.parametrize("dt", [
    "2100-01-01T00:00:00+01:00",
    datetime.datetime(2100, 1, 1, tzinfo=ZoneInfo("Europe/Stockholm")),
])
def test_PastDateTime_raise(dt):
    class Test(Model):
        dt: AwarePastDateTime

    with pytest.raises(ValidationError, match="valid"):
        Test(dt=dt)


# ======================================================
### Tests for DateTimePeriod()

def test_DateTimePeriod():
    datetime_period = DateTimePeriod(start_datetime=end_datetime, end_datetime=start_datetime)
    assert datetime_period.span == start_datetime - end_datetime
    assert datetime_period.as_tuple() == (end_datetime, start_datetime)
    assert datetime_period.as_tuple(sort=True) == (start_datetime, end_datetime)
