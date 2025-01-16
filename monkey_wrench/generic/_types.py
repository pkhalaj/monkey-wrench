"""The module providing the common types that will be used in other sub-packages."""

from typing import TypeVar, Union

T = TypeVar("T")
ListSetTuple = Union[list[T], set[T], tuple[T, ...]]
"""Parametric type alias for the union of lists, sets, tuple.

Note:
    Strings and dictionaries have been intentionally left out!
"""

StringOrStrings = str | list[str]
"""Type alias for a string or a list of strings that will be used e.g. as a pattern to search in other strings."""
