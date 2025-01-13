"""The module providing common functions used in other modules."""

from typing import Any, Callable

from pydantic import validate_call

from monkey_wrench.generic._types import ListSetTuple, StringOrStrings


@validate_call()
def apply_to_single_or_all(func: Callable, single_item_or_items: ListSetTuple | dict | Any) -> Any:
    """Apply the given function to all items of the input, if it is a dict/list/set/tuple, or only on the single input.

    Note:
        In case of a dictionary, ``func`` will be applied on the values.

    Warning:
        A string, although being a sequence, is treated as a single item.

    Args:
        func:
            The function to be applied.
        single_item_or_items:
            Either a single item or a dict/list/set/tuple of items.

    Returns:
        Either a single output or a dict/list/set/tuple of outputs, resulting from applying the given function.

    Example:
        >>> from monkey_wrench.generic import apply_to_single_or_all
        >>>
        >>> apply_to_single_or_all(lambda x: x**2, [1, 2, 3])
        [1, 4, 9]
        >>> apply_to_single_or_all(lambda x: x**2, (1, 2, 3))
        (1, 4, 9)
        >>> apply_to_single_or_all(lambda x: x**2, {"a": 1, "b": 2, "c":3})
        {'a': 1, 'b': 4, 'c': 9}
        >>> apply_to_single_or_all(lambda x: x**2, 3)
        9
        >>> apply_to_single_or_all(lambda x: x*2, "book!")
        'book!book!'
    """
    match single_item_or_items:
        case list():
            return [func(i) for i in single_item_or_items]
        case set():
            return {func(i) for i in single_item_or_items}
        case tuple():
            return tuple(func(i) for i in single_item_or_items)
        case dict():
            return {k: func(v) for k, v in single_item_or_items.items()}
        case _:
            return func(single_item_or_items)


@validate_call
def get_item_type(single_item_or_items: ListSetTuple[Any] | dict | Any) -> Any:
    """Return the type of the single item, or any item in case of a dict/list/set/tuple of items.

    Note:
        In case of a dictionary, the type of values will be considered.

    Warning:
        In case of a dict/list/set/tuple, it is assumed that all items have the same type. This function does not
        perform any checks regarding the order of items or that all items have the same type.

    Args:
        single_item_or_items:
            Either a single item or a dict/list/set/tuple of items.

    Returns:
        Either the type of the single input, or the type of an item from the dict/list/set/tuple.

    Raises:
        ValueError:
            If the given input is an empty dict/list/set/tuple.

    Example:
        >>> from monkey_wrench.generic import get_item_type
        >>> get_item_type([3, 2, 1])
        <class 'int'>
        >>> # Note that the types differ and the function does not check this!
        >>> get_item_type((3.0, 2, 1))
        <class 'float'>
        >>> get_item_type(3)
        <class 'int'>
    """
    match single_item_or_items:
        case dict() | list() | set() | tuple():
            if len(single_item_or_items) == 0:
                raise ValueError("Empty iterable!")
            if isinstance(single_item_or_items, dict):
                single_item_or_items = single_item_or_items.values()
            return type(list(single_item_or_items)[0])
        case _:
            return type(single_item_or_items)


@validate_call
def pattern_exists(
        item: str, pattern: StringOrStrings | None = None, match_all: bool = True, case_sensitive: bool = True
) -> bool:
    """Check if a string or a list of strings exists in the given item.

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
        >>> from monkey_wrench.generic import pattern_exists
        >>>
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
