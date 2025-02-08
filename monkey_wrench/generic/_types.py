from typing import TypeVar, Union

from pydantic import BaseModel

T = TypeVar("T")

ListSetTuple = Union[list[T], set[T], tuple[T, ...]]
"""Parametric type alias for the union of lists, sets, and tuples, i.e. classic iterables.

Warning:
    Strings and dictionaries have been intentionally left out, although they are also iterables!
"""


class Model(BaseModel, extra="forbid"):
    """A Pydantic model to be used as a base for all other models.

    Note:
        When initializing models that inherit from ``Model``, an exception will be raised if any extra keyword arguments
        are passed to the constructor. Extra keyword arguments correspond to extra fields that have not been explicitly
        defined in the model.

    Example:
        >>> class Dataset(Model):
        ...     name: str
        >>>
        >>> # The following will lead to an exception, since `number` has not been explicitly defined as a model field.
        >>> dataset = Dataset(name="dataset-name", number=1)
    """
    pass
