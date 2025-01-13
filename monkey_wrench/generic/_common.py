"""The module providing common functions used in other modules."""

from typing import Any, Callable

from pydantic import validate_call

from monkey_wrench.generic._types import ListSetTuple, StringOrStrings


@validate_call()
def apply_to_single_or_collection(func: Callable, single_or_collection: ListSetTuple | dict | Any) -> Any:
    """Apply the given function to a single item or all elements of a collection (dict/list/set/tuple).

    Note:
        In case of a dictionary, ``func`` will be applied on the values.

    Warning:
        A string, although being a collection, is treated as a single item.

    Args:
        func:
            The function to be applied.
        single_or_collection:
            Either a single item or a collection (dict/list/set/tuple).

    Returns:
        Either a single output or a collection as output, resulting from applying the given function.

    Example:
        >>> apply_to_single_or_collection(lambda x: x**2, [1, 2, 3])
        [1, 4, 9]

        >>> apply_to_single_or_collection(lambda x: x**2, (1, 2, 3))
        (1, 4, 9)

        >>> apply_to_single_or_collection(lambda x: x**2, {"a": 1, "b": 2, "c":3})
        {'a': 1, 'b': 4, 'c': 9}

        >>> apply_to_single_or_collection(lambda x: x**2, set())
        set()

        >>> apply_to_single_or_collection(lambda x: x**2, 3)
        9

        >>> apply_to_single_or_collection(lambda x: x*2, "book!")
        'book!book!'
    """
    match single_or_collection:
        case list():
            return [func(i) for i in single_or_collection]
        case set():
            return {func(i) for i in single_or_collection}
        case tuple():
            return tuple(func(i) for i in single_or_collection)
        case dict():
            return {k: func(v) for k, v in single_or_collection.items()}
        case _:
            return func(single_or_collection)


@validate_call
def element_type(single_or_collection: ListSetTuple[Any] | dict | Any) -> Any:
    """Return the type of the single item, or any element in case of a collection (dict/list/set/tuple).

    Note:
        In case of a dictionary, the type of values will be considered.

    Warning:
        In case of a collection, it is assumed that all elements have the same type. This function does not
        perform any checks regarding the order of elements or that they all have the same type.

    Args:
        single_or_collection:
            Either a single item or a collection (dict/list/set/tuple).

    Returns:
        Either the type of the single input, or the type of an element from the collection. In case of an empty
        collection, ``None`` is returned.

    Example:
        >>> element_type([3, 2, 1])
        <class 'int'>

        >>> # Note that the types differ and the function does not check this!
        >>> element_type((3.0, 2, "1"))
        <class 'float'>

        >>> element_type(3)
        <class 'int'>

        >>> element_type(set()) is None
        True
    """
    match single_or_collection:
        case dict() | list() | set() | tuple():
            if len(single_or_collection) == 0:
                return None
            if isinstance(single_or_collection, dict):
                single_or_collection = single_or_collection.values()
            return type(list(single_or_collection)[0])
        case _:
            return type(single_or_collection)


@validate_call
def pattern_exists(
        item: str, pattern: StringOrStrings | None = None, match_all: bool = True, case_sensitive: bool = True
) -> bool:
    """Check if a string or a list of strings exist(s) in the given item.

    Args:
        item:
            The string in which the pattern will be looked for.
        pattern:
            The pattern to look for. It can be either a single string, a list of strings, or  ``None.``.
            Defaults to ``None``, which means that the function returns ``True``.
        match_all:
            A boolean indicating whether to match all pattern items in case of a pattern list. Defaults to ``True``.
            When it is set to ``False``, only one match suffices. In the case of a single string this parameter does
            not have any effect.
        case_sensitive:
            A boolean indicating whether to perform a case-sensitive match. Defaults to ``True``.

    Returns:
        A boolean indicating whether all or any (depending on ``match_all``) of the pattern items exist(s) in the given
        item.

    Examples:
        >>> pattern_exists("abcde")
        True

        >>> pattern_exists("abcde", pattern="ab")
        True

        >>> pattern_exists("abcde", pattern="A", case_sensitive=False)
        True

        >>> pattern_exists("abcde", pattern=["A", "b"], match_all=False)
        True

        >>> pattern_exists("abcde", pattern=["A", "b"], match_all=True)
        False

        >>> pattern_exists("abcde", pattern=["A", "b"], match_all=True, case_sensitive=False)
        True
    """
    if pattern is None:
        return True

    if not isinstance(pattern, list):
        pattern = [pattern]

    if not case_sensitive:
        item = item.lower()
        pattern = [i.lower() for i in pattern]

    func = all if match_all is True else any
    return func(i in item for i in pattern)
