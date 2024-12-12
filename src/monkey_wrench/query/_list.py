"""The module which defines the class for querying lists."""
from datetime import datetime
from typing import Any, Generator, Self, Type, TypeVar

import numpy as np
from pydantic import PositiveInt, validate_call

from monkey_wrench.date_time import DateTimeParser, assert_start_time_is_before_end_time

from ._common import Query

T = TypeVar("T")


class List[T](Query):
    """A class to provide generic functionalities to query lists.

    Note:
        This class is meant to behave as an immutable list.

    Note:
        This class utilizes ``numpy.ndarray`` objects under the hood.
    """

    @validate_call
    def __init__(
            self,
            items: list[T],
            datetime_parser: Type[DateTimeParser],
            log_context: str = "List"
    ) -> None:
        """Make an instance of the class.

        Args:
            items:
                The complete list of items to query.
            datetime_parser:
                A class of type :class:`~monkey_wrench.date_time.DateTimeParser` to enable parsing items into
                datetime objects.
            log_context:
                A string that will be used in log messages to determine the context. Defaults to empty string.
        """
        super().__init__(log_context=log_context)

        if len(items) == 0:
            raise ValueError("List is empty and there are no items to query!")

        try:
            self.__parser_vectorized = np.vectorize(datetime_parser.parse)
            self.__items_vector = np.array(items)
            self.__items_parsed = self.__parser_vectorized(self.__items_vector)
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Could not parse items using the provided datetime parser.") from None
            else:
                raise e

    def __iter__(self) -> Generator[T, None, None]:
        """Implement iteration over the items in the List object."""
        for item in self.__items_vector:
            yield item

    def __eq__(self, other: Any) -> bool:
        """Implement the equality comparison operator, i.e. ``==``."""
        for i, j in zip(self, other, strict=False):
            if i != j:
                return False
        return True

    def __getitem__(self, *indices) -> "List":
        """Get a new ``List`` object from the given indices."""
        new_list = List.__new__(List)
        super(List, new_list).__init__(log_context=self._log_context)

        new_list.__items_vector = self.__items_vector[indices]
        new_list.__items_parsed = self.__items_parsed[indices]

        return new_list

    def __str__(self) -> str:
        """Get the string representation of the List object."""
        return str(self.__items_vector)

    @staticmethod
    def len(item: "List") -> int:
        """Return the number of items in the List object."""
        return item.__items_vector.shape[0]

    @validate_call
    def to_python_list(self) -> list[T]:
        """Convert the List object into a Python built-in list object."""
        return self.__items_vector.tolist()

    @validate_call
    def query(self, start_datetime: datetime, end_datetime: datetime) -> Self:
        """Query items from the List object, given a start datetime and an end datetime.

        Args:
            start_datetime:
                The start datetime to query (inclusive).
            end_datetime:
                The end datetime to query (exclusive).

        Returns:
            A new List object including items that match the given query.

        Raises:
            ValueError:
                Refer to :func:`~monkey_wrench.date_time.assert_start_time_is_before_end_time`.
        """
        return self[self.__get_indices(start_datetime, end_datetime)]

    @validate_call
    def query_indices(self, start_datetime: datetime, end_datetime: datetime) -> list[int]:
        """Similar to :func:`List.query`, but returns the indices of items instead."""
        return self.__get_indices(start_datetime, end_datetime).tolist()

    @validate_call
    def __get_indices(self, start_datetime: datetime, end_datetime: datetime) -> np.array:
        """Similar to :func:`List.query_indices`, but returns the numpy indices instead."""
        assert_start_time_is_before_end_time(start_datetime, end_datetime)
        idx = np.where((self.__items_parsed >= start_datetime) & (self.__items_parsed < end_datetime))
        return idx[0]

    @validate_call
    def normalize_index(self, index: int) -> int:
        """Convert a negative index into its positive equivalent, or return the original index if it is non-negative.

        Raises:
            IndexError:
                If the positive index or its positive equivalent exceeds the size of the List object.
        """
        n_total = List.len(self)
        if index < 0:
            index += n_total

        if index < 0 or index >= n_total:
            raise IndexError("Index is out of range.")

        return index

    @validate_call
    def generate_k_sized_batches_by_index(
            self, k: PositiveInt, index_start: int = 0, index_end: int = -1, as_python_lists: bool = True
    ) -> Generator[list, None, None] | Generator["List", None, None]:
        """Return batches (sub-lists) of size ``k`` and move forward by ``1`` index each time.

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
            as_python_lists:
                A boolean determining whether to return each batch as a Python built-in list or as ``List`` objects.
                Defaults to ``True``.

        Yields:
            A generator that yields batches of size ``k``. Adjacent batches overlap by ``k-2`` items.

        Raises:
            ValueError:
                If ``index_start`` is greater than ``index_end``.
            ValueError:
                If ``k`` exceeds the size of the list.
            IndexError:
                If normalized indices exceed the size of the List object. Refer to :obj:`~List.normalize_index`.
        """
        n_total = List.len(self)

        if n_total < k:
            raise ValueError("Batch size exceeds number of items in list.")

        index_start = self.normalize_index(index_start)
        index_end = self.normalize_index(index_end)
        if index_start > index_end:
            raise ValueError("`index_start` cannot be greater than `index_end`.")

        index = index_start
        while index <= index_end:
            if index <= k - 1:
                index = k - 1
            batch = self.__items_vector[index - k + 1: index + 1]
            yield batch.tolist() if as_python_lists else batch
            index += 1
