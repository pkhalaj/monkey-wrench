"""The module providing common functions used in other modules."""

from typing import Any, Callable

from pydantic import validate_call

from monkey_wrench.generic._types import IterableContainer


@validate_call()
def apply_to_single_or_all(func: Callable, single_item_or_items: IterableContainer | dict | Any) -> Any:
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
def get_item_type(single_item_or_items: IterableContainer[Any] | dict | Any) -> Any:
    """Return the type of the single item, or any item in case of a dict/list/set/tuple of items.

    Note:
        In case of a dictionary, the type of values will be considered.

    Warning:
        In case of an iterable, it is assumed that all items have the same type. This function does not perform any
        checks regarding the order of items or that all items have the same type.

    Args:
        single_item_or_items:
            Either a single item or a dict/list/set/tuple of items.

    Returns:
        Either the type of the single input, or the type of an item from the iterable.

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
                raise ValueError("Empty iterable")
            if isinstance(single_item_or_items, dict):
                single_item_or_items = single_item_or_items.values()
            return type(list(single_item_or_items)[0])
        case _:
            return type(single_item_or_items)
