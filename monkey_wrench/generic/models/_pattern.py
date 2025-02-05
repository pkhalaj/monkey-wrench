from typing import Any, Callable, Iterable

from pydantic import AfterValidator, validate_call
from typing_extensions import Annotated

from monkey_wrench.generic._types import Model

Strings = Annotated[str | list[str], AfterValidator(lambda x: [x] if isinstance(x, str) else x)]
"""Type annotation and Pydantic validator to represent (convert to) a list of strings.

In the case of a single string, it will be enclosed in a list.
"""


class Pattern(Model):
    """Pydantic model for patterns."""

    sub_strings: Strings | None = None
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
    def match_function(self) -> Callable[[Iterable[object]], bool]:
        """Return either ``all()`` or ``any()`` depending on the value of :attr:`Pattern.match_all`."""
        return all if self.match_all else any

    @validate_call
    def exists_in(self, item: Any) -> bool:
        """Check if the pattern exists in the given item.

        Args:
            item:
                The string in which the sub-strings will be looked for. If item is not a string, it will be first
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
        item = str(item)

        if self.sub_strings is None:
            return True

        _sub_strings = self.sub_strings[:]

        if not self.case_sensitive:
            item = item.lower()
            _sub_strings = [s.lower() for s in _sub_strings]

        return self.match_function(p in item for p in _sub_strings)

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
