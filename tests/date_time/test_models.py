import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest
from pydantic import ValidationError

from monkey_wrench.date_time import DateTimeDict, DateTimePeriod, PastDateTime, TimeDeltaDict, TimeInterval, ZoneInfo_
from monkey_wrench.generic import Model

from .const import end_datetime, start_datetime

# ======================================================
### Tests for DateTimePeriod():

def test_DateTimePeriod():
    datetime_period = DateTimePeriod(start_datetime=end_datetime, end_datetime=start_datetime)
    assert datetime_period.span == start_datetime - end_datetime
    assert datetime_period.start_datetime == end_datetime
    assert datetime_period.end_datetime == start_datetime
    assert datetime_period.as_tuple() == (end_datetime, start_datetime)
    assert datetime_period.as_tuple(sort=True) == (start_datetime, end_datetime)


# ======================================================
### Tests for ZoneInfo_()

@pytest.mark.parametrize("timezone", [
    "UTC",
    "Europe/Stockholm"
])
def test_ZoneInfo(timezone):
    class Test(Model):
        tz_info: ZoneInfo_

    assert Test(tz_info=timezone).tz_info == ZoneInfo(timezone)


def test_ZoneInfo_raise():
    class Test(Model):
        tz_info: ZoneInfo_

    with pytest.raises(ZoneInfoNotFoundError, match="found"):
        Test(tz_info="invalid")


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
### Tests for DateTimeDict()

def test_DateTimeDict():
    dt_list = [2022, 1, 1]
    timezone = "Europe/Stockholm"
    dt_dict = DateTimeDict(datetime=dt_list, timezone=timezone)
    assert dt_dict.timezone == ZoneInfo(timezone)
    assert dt_dict.timezone_aware_datetime == datetime.datetime(*dt_list, tzinfo=ZoneInfo(timezone))


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
### Tests for PastDateTime()

@pytest.mark.parametrize("dt", [
    dict(datetime=[2000, 1, 1], timezone="Europe/Stockholm"),
    datetime.datetime(2000, 1, 1, tzinfo=ZoneInfo("Europe/Stockholm")),
])
def test_PastDateTime(dt):
    class Test(Model):
        dt: PastDateTime

    assert Test(dt=dt).dt == datetime.datetime(2000, 1, 1, tzinfo=ZoneInfo("Europe/Stockholm"))


@pytest.mark.parametrize("dt", [
    dict(datetime=[2100, 1, 1], timezone="Europe/Stockholm"),
    datetime.datetime(2100, 1, 1, tzinfo=ZoneInfo("Europe/Stockholm")),
])
def test_PastDateTime_raise(dt):
    class Test(Model):
        dt: PastDateTime

    with pytest.raises(ValidationError, match="valid"):
        Test(dt=dt)
