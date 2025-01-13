"""The module to define constant values to be used for testing the `date_time` package."""

from datetime import datetime, timedelta

start_datetime = datetime(2020, 1, 1)
end_datetime = datetime(2021, 1, 1)
interval = timedelta(days=30)
remainder = (end_datetime - start_datetime) % interval
quotient = (end_datetime - start_datetime) // interval
