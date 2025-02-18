from typing import Any, Callable, TypeVar

from pydantic import validate_call

from monkey_wrench.generic._types import ListSetTuple

T = TypeVar("T")
U = TypeVar("U")
R = TypeVar("R")


def assert_(item: T, message: str, exception: type[Exception] = ValueError, silent: bool = True) -> T:
    """Assert the truth value of the item, and return the item or raise ``exception``.

    Args:
        item:
            The item to assert. It does not have to be a boolean. For example, given an empty list, ``assert []`` fails
            as an empty list evaluates to ``False``.
        message:
            The exception message, which will be shown when the exception is raised.
        exception:
            The exception to raise if both the ``item`` and ``silent`` evaluate to ``False``.
            Defaults to ``ValueError``.
        silent:
            A boolean indicating whether to return the item silently or raise an exception in the case of assertion
            failure. Defaults to ``True``, which means the item will be silently returned.

    Returns:
        Return the item if it evaluates to ``True``. If the item evaluates to ``False``, return it only if ``silent``
        is ``True``.

    Raises:
        ``exception``:
            If the ``item`` evaluates to ``False`` and ``silent`` is ``False``.
    """
    if item or silent:
        return item
    raise exception(message)


@validate_call
def apply_to_single_or_collection(
        function: Callable[[T], R],
        single_or_collection: dict[Any, T] | ListSetTuple[T] | T
) -> dict[Any, R] | ListSetTuple[R] | R:
    """Apply the given function to a single item or all elements of a collection (dict/list/set/tuple).

    Note:
        In the case of a dictionary, ``function`` will be applied to the values.

    Warning:
        A string, although being a collection, is treated as a single item.

    Args:
        function:
            The function to be applied.
        single_or_collection:
            Either a single item or a collection (dict/list/set/tuple).

    Returns:
        Either a single output, or a collection as output resulting from applying the given function.

    Examples:
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
        case dict():
            return {k: function(v) for k, v in single_or_collection.items()}
        case list():
            return [function(i) for i in single_or_collection]
        case set():
            return {function(i) for i in single_or_collection}
        case tuple():
            return tuple(function(i) for i in single_or_collection)
        case _:
            return function(single_or_collection)


@validate_call
def collection_element_type(collection: dict[Any, T] | ListSetTuple[T]) -> T:
    """Return the type of collection elements, e.g. for ``set[T]`` it returns ``T``.

    Args:
        collection:
            The collection to get the type of any element from.

    Returns:
        The type of any element from the collection (dict/list/set/tuple). In the case of an empty collection, ``None``
        is returned.

    Raises:
        TypeError:
            If the collection elements are of different types.

    Examples:
        >>> collection_element_type([3, 2, 1])
        <class 'int'>

        >>> collection_element_type(set()) is None
        True

        >>> # The following will lead to an exception, since the collection elements are not of the same type.
        >>> # element_type_from_collection((3.0, 2.0, "1"))
    """
    if len(collection) == 0:
        return None

    if isinstance(collection, dict):
        collection = collection.values()

    collection = tuple(collection)
    any_element_type = type(collection[0])

    if all([isinstance(e, any_element_type) for e in collection]):
        return any_element_type

    raise TypeError("Cannot return a single element type when collection elements are of different types.")


@validate_call
def type_(single_or_collection: dict[Any, T] | ListSetTuple[T] | T) -> T:
    """Return the type of the given item, or any element from the collection using :func:`element_type_from_collection`.

    Examples:
        >>> type_([3, 2, 1])
        <class 'int'>

        >>> type_(3)
        <class 'int'>
    """
    match single_or_collection:
        case dict() | list() | set() | tuple():
            return collection_element_type(single_or_collection)
        case _:
            return type(single_or_collection)
