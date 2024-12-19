"""Module providing common utilities used in other modules."""

from typing import Any, Callable

from pydantic import validate_call


@validate_call
def apply_to_single_or_all(func: Callable, single_item_or_items: list | dict | set | tuple | Any) -> Any:
    """Apply the given function to all items of the input (if it is a list/dict/set/tuple), or only on the single input.

    Note:
        In case of a dictionary, the func will be applied on the values.

    Args:
        func:
            The function to be applied.
        single_item_or_items:
            Either a single item or a list/dict/set/tuple of items.

    Returns:
        Either a single output or a list/dict/set/tuple of outputs, resulting from applying the given function.

    Example:
        >>> from monkey_wrench.generic import apply_to_single_or_all
        >>> apply_to_single_or_all(lambda x: x**2, [1, 2, 3])
        [1, 4, 9]
        >>> apply_to_single_or_all(lambda x: x**2, (1, 2, 3))
        (1, 4, 9)
        >>> apply_to_single_or_all(lambda x: x**2, {"a": 1, "b": 2, "c":3})
        {"a": 1, "b": 4, "c": 9}
        >>> apply_to_single_or_all(lambda x: x**2, 3)
        9
    """
    match single_item_or_items:
        case list():
            return [func(i) for i in single_item_or_items]
        case set():
            return {func(i) for i in single_item_or_items}
        case tuple():
            return tuple([func(i) for i in single_item_or_items])
        case dict():
            return {k: func(v) for k, v in single_item_or_items.items()}
        case _:
            return func(single_item_or_items)


@validate_call
def return_single_or_first(single_item_or_items: Any) -> Any:
    """Return the first item from the input if it is a list/tuple, otherwise return the input itself.

    Warning:
        This function raises an exception for sets and dictionaries, as they are not ordered and the concept of the
        first element does not apply.

    Args:
        single_item_or_items:
            Either a single item or a list/tuple of items.

    Returns:
        Either the given single input as it is, or the first item from the input if it is a list/tuple. An empty
        list/tuple will be returned as it is.

    Raises:
        ValueError:
            If the given input is a set or a dictionary.

    Example:
        >>> from monkey_wrench.generic import return_single_or_first
        >>> return_single_or_first([3, 2, 1])
        2
        >>> return_single_or_first((3, 2, 1))
        3
        >>> return_single_or_first(3)
        3
        >>> return_single_or_first([])
        []
    """
    if single_item_or_items in [[], ()]:
        return single_item_or_items

    match single_item_or_items:
        case set() | dict():
            raise ValueError("Cannot return the first item from a `set` or a `dictionary`.")
        case list() | tuple():
            return single_item_or_items[0]
        case _:
            return single_item_or_items
