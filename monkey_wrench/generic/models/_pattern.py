from typing import Any, Callable, Iterable, TypeVar, assert_never, cast

from pydantic import validate_call

from monkey_wrench.generic._common import apply_to_single_or_collection
from monkey_wrench.generic._types import ListSetTuple, Model
from monkey_wrench.generic.models._function import TransformFunction

OriginalType = TypeVar("OriginalType")
TransformedType = TypeVar("TransformedType")


class StringTransformation[OriginalType, TransformedType](Model):
    """Pydantic model for transformations on strings, e.g. before writing to or after reading from a file."""

    trim: bool = True
    """A boolean indicating whether to remove trailing/leading whitespaces, tabs, and newlines from string items.

    Defaults to ``True``.
    """

    transform_function: TransformFunction[TransformedType] | None = None
    """If given, each item will be transformed according to the function.

    Defaults to ``None``, which means no transformation is performed and items will be treated as they are.
    """

    @validate_call
    def _transform_item(self, item: OriginalType) -> OriginalType | TransformedType:
        """Transform a single item."""
        return self.transform_function(item) if self.transform_function is not None else item

    @validate_call
    def transform_items(
            self, items: ListSetTuple[OriginalType] | OriginalType
    ) -> ListSetTuple[TransformedType] | ListSetTuple[OriginalType] | OriginalType | TransformedType:
        """Transform a single or multiple items (of any type)."""
        return cast(
            ListSetTuple[TransformedType] | ListSetTuple[OriginalType] | OriginalType | TransformedType,
            apply_to_single_or_collection(self._transform_item, items)
        )

    @validate_call
    def _trim_item(self, item: OriginalType) -> str:
        """Trim a single item. The item can be of any type and will be coerced into a string first."""
        item_str = str(item)
        return item_str.strip() if self.trim else item_str

    @validate_call
    def trim_items(self, items: ListSetTuple[OriginalType] | OriginalType) -> ListSetTuple[str] | str:
        """Trim a single or multiple items. The items can be of any type and will be first coerced into strings."""
        return cast(
            ListSetTuple[str],
            apply_to_single_or_collection(self._trim_item, items)
        )


class Pattern(Model):
    """Pydantic model for finding sub-strings in other strings."""

    negate: bool = False
    """A boolean indicating whether the result of pattern matching should be negated, i.e. one needs a non-match.

    In other words, the result of match will be always XORed (^) with this boolean. Defaults to ``False``, which means
    the result will not be negated.
    """

    sub_strings: str | list[str] | None = None
    """The sub-strings to look for. It can be either a single string, a list of strings, or  ``None.``.

    Defaults to ``None``, which means :func:`check` returns ``True`` if ``negate`` is also ``False``.
    """

    case_sensitive: bool = True
    """A boolean indicating whether to perform a case-sensitive match. Defaults to ``True``."""

    match_all: bool = True
    """A boolean indicating whether to match all or any of the sub-strings. Defaults to ``True``.

    When it is set to ``False``, only one match suffices. In the case of a single sub-string this parameter does not
    have any effect.
    """

    @property
    def pattern(self) -> "Pattern":
        return Pattern(sub_strings=self.sub_strings, case_sensitive=self.case_sensitive, match_all=self.match_all)

    @property
    def sub_strings_list(self) -> list[str]:
        """Enclose ``sub_strings`` in a list, if there is only a single sub-string."""
        match self.sub_strings:
            case None:
                return []
            case list():
                return self.sub_strings
            case str():
                return [self.sub_strings]
            case _:
                assert_never(self.sub_strings)

    @property
    def match_function(self) -> Callable[[Iterable[object]], bool]:
        """Return either ``all()`` or ``any()`` built-in function depending on :attr:`Pattern.match_all`."""
        return all if self.match_all else any

    @validate_call
    def check(self, item: Any) -> bool:
        """Check if the pattern exists in the given item.

        Args:
            item:
                The string in which the sub-strings will be looked for. If the item is not a string, it will be first
                converted to a string.

        Returns:
            A boolean indicating whether all or any (depending on :attr:`Pattern.match_all`) of the sub-strings exist(s)
            in the given item.

        Examples:
            >>> Pattern().check("abcde")
            True

            >>> Pattern(sub_strings="ab").check("abcde")
            True

            >>> Pattern(sub_strings="A", case_sensitive=False).check("abcde")
            True

            >>> Pattern(sub_strings=["A", "b"], match_all=False).check("abcde")
            True

            >>> Pattern(sub_strings=["A", "b"], match_all=True).check("abcde")
            False

            >>> Pattern(sub_strings=["A", "b"], match_all=True, case_sensitive=False).check("abcde")
            True
        """
        if self.sub_strings is None:
            return True ^ self.negate

        item = str(item)
        _sub_strings = self.sub_strings_list[:]

        if not self.case_sensitive:
            item = item.lower()
            _sub_strings = [s.lower() for s in _sub_strings]

        return self.match_function(s in item for s in _sub_strings) ^ self.negate

    @validate_call
    def __ror__(self, other: str) -> bool:
        """Syntactic sugar for :func:`check`.

        Examples:
            >>> "abcde" | Pattern()
            True

            >>> "abcde" | Pattern(sub_strings=["A", "b"], match_all=True)
            False
        """
        return self.check(other)
