"""The module to define constant values to be used for testing :obj:`datetime_utils` package."""

from datetime import datetime, timedelta

START_DATETIME = datetime(2020, 1, 1)
END_DATETIME = datetime(2021, 1, 1)
INTERVAL = timedelta(days=30)
REMAINDER = (END_DATETIME - START_DATETIME) % INTERVAL
QUOTIENT = (END_DATETIME - START_DATETIME) // INTERVAL
