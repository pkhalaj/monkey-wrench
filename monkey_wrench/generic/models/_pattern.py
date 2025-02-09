from typing import Any, Callable, Iterable

from pydantic import validate_call

from monkey_wrench.generic._types import Specifications


class Pattern(Specifications):
    """Pydantic model for finding sub-strings in other strings."""

    sub_strings: str | list | None = None
    """The sub-strings to look for. It can be either a single string, a list of strings, or  ``None.``.

    Defaults to ``None``, which means :func:`exists_in` returns ``True``.
    """

    case_sensitive: bool = True
    """A boolean indicating whether to perform a case-sensitive match. Defaults to ``True``."""

    match_all: bool = True
    """A boolean indicating whether to match all or any of the sub-strings. Defaults to ``True``.

    When it is set to ``False``, only one match suffices. In the case of a single sub-string this parameter does not
    have any effect.
    """

    @property
    def sub_strings_list(self):
        """Enclose ``sub_strings`` in a list, if there is only a single sub-string."""
        return self.sub_strings if isinstance(self.sub_strings, list) else [self.sub_strings]

    @property
    def match_function(self) -> Callable[[Iterable[object]], bool]:
        """Return either ``all()`` or ``any()`` built-in function depending on :attr:`Pattern.match_all`."""
        return all if self.match_all else any

    @validate_call
    def exists_in(self, item: Any) -> bool:
        """Check if the pattern exists in the given item.

        Args:
            item:
                The string in which the sub-strings will be looked for. If the item is not a string, it will be first
                converted to a string.

        Returns:
            A boolean indicating whether all or any (depending on :attr:`Pattern.match_all`) of the sub-strings exist(s)
            in the given item.

        Examples:
            >>> Pattern().exists_in("abcde")
            True

            >>> Pattern(sub_strings="ab").exists_in("abcde")
            True

            >>> Pattern(sub_strings="A", case_sensitive=False).exists_in("abcde")
            True

            >>> Pattern(sub_strings=["A", "b"], match_all=False).exists_in("abcde")
            True

            >>> Pattern(sub_strings=["A", "b"], match_all=True).exists_in("abcde")
            False

            >>> Pattern(sub_strings=["A", "b"], match_all=True, case_sensitive=False).exists_in("abcde")
            True
        """
        if self.sub_strings is None:
            return True

        item = str(item)
        _sub_strings = self.sub_strings_list[:]

        if not self.case_sensitive:
            item = item.lower()
            _sub_strings = [s.lower() for s in _sub_strings]

        return self.match_function(s in item for s in _sub_strings)

    @validate_call
    def __ror__(self, other: str) -> bool:
        """Syntactic sugar for :func:`exists_in`.

        Examples:
            >>> "abcde" | Pattern()
            True

            >>> "abcde" | Pattern(sub_strings=["A", "b"], match_all=True)
            False
        """
        return self.exists_in(other)
