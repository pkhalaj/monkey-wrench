"""The module which defines the class for querying lists."""

from datetime import datetime
from typing import Generator, Type, TypeVar

import numpy as np
from pydantic import PositiveInt, validate_call

from monkey_wrench.datetime_utils import DateTimeParser, assert_start_time_is_before_end_time

from ._common import Query

T = TypeVar("T")


class List[T](Query):
    """A class to provide generic functionalities to query lists."""

    @validate_call
    def __init__(self, items: list[T], datetime_parser: Type[DateTimeParser], log_context: str = "List") -> None:
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
        self.__n_total = len(items)

        if self.__n_total == 0:
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

    @validate_call
    def len(self, item: list[T]) -> int:
        """Return the number of items in the list."""
        return len(item)

    @validate_call
    def query(self, start_datetime: datetime, end_datetime: datetime) -> list[T]:
        """Query items from the list, given a start datetime and an end datetime.

        Args:
            start_datetime:
                The start datetime to query (inclusive).
            end_datetime:
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

    @validate_call
    def query_indices(self, start_datetime: datetime, end_datetime: datetime) -> list[int]:
        """Similar to :func:`List.query`, but returns the indices of items instead."""
        assert_start_time_is_before_end_time(start_datetime, end_datetime)
        idx = np.where((self.__items_parsed >= start_datetime) & (self.__items_parsed < end_datetime))
        return idx[0].tolist()

    @validate_call
    def normalize_index(self, index: int) -> int:
        """Convert a negative index into its positive equivalent, or return the original index if it is non-negative.

        Raises:
            IndexError:
                If the positive index or its positive equivalent exceeds the size of the list.
        """
        if index < 0:
            index += self.__n_total

        if index < 0 or index >= self.__n_total:
            raise IndexError("Index is out of range.")

        return index

    @validate_call
    def generate_k_sized_batches_by_index(
            self, k: PositiveInt, index_start: int = 0, index_end: int = -1,
    ) -> Generator[list, None, None]:
        """Return batches of size ``k`` and move forward by ``1`` index each time.

        A batch consists of the item at the current index, as well as ``k-1`` previous items that immediately proceed
        the current item. In other words, a batch includes ``k`` adjacent items, with the item at the current index
        being the last item of the batch. Next batch is retrieved by moving the current index by ``+1``. As a result,
        two consecutive batches have ``k-2`` common objects.

        Both ``index_start`` and ``index_end`` are considered as inclusive. They can be negative as well.

        Note:
            The indices are zero-based. If ``index_start`` is less than or equal to ``k-1``, the first batch includes
            items from index ``0`` to index ``k-1`` (inclusive). The next batch includes indices ``[1, k]``.

        Args:
            k:
                The size of the batches. Each batch includes the current item as well as ``k-1`` proceeding items.
            index_start:
                The zero-based index of the first item to start generating the batches from. Defaults to ``0`` and can
                be negative as well.
            index_end:
                The zero-based index of the last item (inclusive) up to which the batches are generated.
                Defaults to ``-1`` meaning the last item of the list makes the last item of the final batch.

        Yields:
            A generator that yields batches of size ``k``. Adjacent batches overlap by ``k-2`` items.

        Raises:
            ValueError:
                If ``index_start`` is greater than ``index_end``.
            ValueError:
                If ``k`` exceeds the size of the list.
            IndexError:
                Refer to :obj:`List.normalize_index`.
        """
        if self.__n_total < k:
            raise ValueError("Batch size exceeds number of items in list.")

        index_start = self.normalize_index(index_start)
        index_end = self.normalize_index(index_end)
        if index_start > index_end:
            raise ValueError("`index_start` cannot be greater than `index_end`.")

        index = index_start
        while index <= index_end:
            if index <= k - 1:
                index = k - 1
            yield self.__items[index - k + 1: index + 1]
            index += 1
