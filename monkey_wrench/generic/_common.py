"""Module providing common utilities used in other modules."""

from typing import Any, Callable

from pydantic import validate_call


@validate_call
def apply_to_single_or_all(func: Callable, single_item_or_items: Any) -> Any:
    """Apply the given function to all items of the input (if it is a list/tuple), or only on the single input.

    Args:
        func:
            The function to be applied.
        single_item_or_items:
            Either a single item or a list/tuple of items.

    Returns:
        Either a single output or a list of outputs, resulting from applying the given function.

    Example:
        >>> from monkey_wrench.generic import apply_to_single_or_all
        >>> apply_to_single_or_all(lambda x: x**2, [1, 2, 3])
        [1, 4, 9]
        >>> apply_to_single_or_all(lambda x: x**2, (1, 2, 3))
        [1, 4, 9]
        >>> apply_to_single_or_all(lambda x: x**2, 3)
        9
    """
    match single_item_or_items:
        case list() | tuple():
            return [func(i) for i in single_item_or_items]
        case _:
            return func(single_item_or_items)


@validate_call
def return_single_or_first(single_item_or_items: Any) -> Any:
    """Return the first item from the input if it is a list/tuple, otherwise return the input itself.

    Args:
        single_item_or_items:
            Either a single item or a list/tuple of items.

    Returns:
        Either the given single input as it is, or the first item from the input if it is a list/tuple. In case of a
        falsy item such as an empty list ``[]``, the falsy item will be returned as it is.

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
    if not single_item_or_items:
        return single_item_or_items

    match single_item_or_items:
        case list() | tuple():
            return single_item_or_items[0]
        case _:
            return single_item_or_items
