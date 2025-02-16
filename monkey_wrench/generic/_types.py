from typing import TypeVar, Union

from pydantic import BaseModel, ConfigDict

ElementType = TypeVar("ElementType")

ListSetTuple = Union[list[ElementType], set[ElementType], tuple[ElementType, ...]]
"""Generic type alias for the union of homogenous lists, sets, and tuples, i.e. classic iterables.

Warning:
    Strings and dictionaries have been intentionally left out, although they are also iterables!
"""


class Model(BaseModel):
    """A Pydantic model to be used as a base for all other models, e.g. specifications of a task.

    Note:
        Models that inherit from this model have the following properties

            1- They do not allow any `extra keyword arguments`_ to be passed to the constructor if the corresponding
            field is not explicitly defined.

            2- The fields are `faux-immutable`_.

            3- They allow for `arbitrary types`_ to be validated, e.g. when using `pydantic.validate_call`_ decorator.

    Example:

        .. code-block:: python

            class Dataset(Model):
                name: str

            # The following will lead to an exception.
            # `number` has not been explicitly defined as a model field.
            dataset = Dataset(name="dataset-name", number=1)

            dataset = Dataset(name="dataset-name")
            # The following will lead to an exception.
            # All fields (i.e. `name` in this case) are immutable.
            dataset.name = "dataset-name_changed"

    .. _pydantic.validate_call: https://docs.pydantic.dev/latest/api/validate_call/
    .. _extra keyword arguments: https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra
    .. _faux-immutable: https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.frozen
    .. _arbitrary types: https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.arbitrary_types_allowed
    """
    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)
