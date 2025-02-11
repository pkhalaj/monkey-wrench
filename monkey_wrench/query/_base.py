from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import NonNegativeInt, validate_call

from monkey_wrench.date_time import DateTimePeriod, DateTimeRangeInBatches
from monkey_wrench.query._types import Batches


class LogMixin:
    @validate_call
    def __init__(self, log_context: str = "") -> None:
        """Make an instance of the class.

        Args:
            log_context:
                A string that will be used in log messages to determine the context. Defaults to an empty string.
        """
        self.__log_context = log_context

    @property
    def log_context(self) -> str:
        """Get the log context as a string."""
        return self.__log_context

    def log_message(self, start_datetime: datetime, end_datetime: datetime, other: str = "") -> None:
        """Log a query message including the start and end datetime values as well as other information (if any)."""
        space = " " if other else ""
        msg = f"{self.log_context} -- Fetch period=['{start_datetime}', '{end_datetime}'){space}{other}".strip()
        logger.info(msg)


class Query(ABC, LogMixin):
    """Abstract base class for queries."""

    def __init__(self, *args, **kwargs) -> None:
        """Make an instance of the class."""
        super().__init__(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def len(items: Any) -> NonNegativeInt:
        """Get the size (number) of items, e.g. the Python built-in ``len()`` function in case of a list."""
        pass

    @abstractmethod
    def query(self, datetime_period: DateTimePeriod) -> Any:
        """Query the specified time period."""
        pass

    def query_in_batches(
            self,
            datetime_range_in_batches: DateTimeRangeInBatches,
            expected_total_count: NonNegativeInt | None = None
    ) -> Batches:
        """Divide the specified time range into smaller intervals (batches) and perform queries on them.

        The arguments are the same as :class:`~monkey_wrench.date_time.DatetimeRangeInBatches`.
        If ``expected_total_count`` is given, it will be compared with ``total_retrieved_count`` and if they are not
        equal a warning will be logged. It defaults to ``None`` which means no comparison is made.

        Yields:
            The result of queries, in the form of 2-tuples in which the first element is the retrieved items from the
            ``query()`` function in each batch and the second element is the size of the items in the batch.
        """
        start_datetime = datetime_range_in_batches.start_datetime
        end_datetime = datetime_range_in_batches.end_datetime
        batch_interval = datetime_range_in_batches.batch_interval

        self.log_message(start_datetime, end_datetime, f"and batch_interval='{batch_interval}'.")
        total_retrieved_count = 0
        for datetime_period in datetime_range_in_batches:
            start, end = datetime_period.as_tuple()
            self.log_message(start, end)
            items = self.query(datetime_period)
            retrieved_count = self.len(items)
            total_retrieved_count += retrieved_count
            self.log_message(start, end, f": retrieved {retrieved_count} items.")
            yield items, retrieved_count

        self.log_message(start_datetime, end_datetime, f": retrieved {total_retrieved_count} items in total.")

        if expected_total_count is not None:
            if expected_total_count != total_retrieved_count:
                logger.warning(f"Expected {expected_total_count} item but retrieved {total_retrieved_count}!")
