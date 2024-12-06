"""The module which defines the class for querying lists."""

from datetime import datetime
from typing import Any, Type

import numpy as np
from pydantic import ConfigDict, validate_call

from monkey_wrench.datetime_utils import DateTimeParser, assert_start_time_is_before_end_time

from ._common import Query


class List(Query):
    """A class to provide generic functionalities to query lists."""

    def __init__(self, items: list[Any], datetime_parser: Type[DateTimeParser], log_context: str = "List") -> None:
        """Make an instance of the class.

        Args:
            items:
                The complete list of items to query.
            datetime_parser:
                A class of type :class:`~monkey_wrench.datetime_utils.DateTimeParser` to enable parsing items into
                datetime objects.
            log_context:
                A string that will be used in log messages to determine the context. Defaults to empty string.
        """
        if len(items) == 0:
            raise ValueError("List is empty and there are no items to query!")

        super().__init__(log_context=log_context)

        self.__items = items
        self.__datetime_parser = datetime_parser

        try:
            self.__parser_vectorized = np.vectorize(datetime_parser.parse)
            self.__items_vector = np.array(self.__items)
            self.__items_parsed = self.__parser_vectorized(self.__items_vector)
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Could not parse items using the provided datetime parser.") from None
            else:
                raise e

    def len(self, item: Any) -> int:
        """Return the number of items in the list."""
        return len(item)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def query(self, start_datetime: datetime, end_datetime: datetime) -> list:
        """Query items from the list, given a start datetime and an end datetime.

        Args:
            start_datetime:
                The start datetime to query (inclusive).
            end_datetime:s
                The end datetime to query (exclusive).

        Returns:
            A filtered list of items which match the given query.

        Raises:
            ValueError:
                Refer to :func:`~monkey_wrench.datetime_utils.assert_start_time_is_before_end_time`.
        """
        assert_start_time_is_before_end_time(start_datetime, end_datetime)
        idx = np.where((self.__items_parsed >= start_datetime) & (self.__items_parsed < end_datetime))
        return self.__items_vector[idx].astype(type(self.__items[0])).tolist()
