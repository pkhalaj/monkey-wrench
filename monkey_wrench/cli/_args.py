"""The module providing the Pydantic model to parse CLI arguments."""

import sys
from typing import ClassVar, Self

from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError


class CommandLineArguments(BaseModel):
    """Pydantic model to validate CLI arguments."""

    task_filepath: ClassVar[str] = ""
    """The path of the task file, which must end in `.yaml` or `.yml`."""

    cli_args: ClassVar[list[str]] = sys.argv
    """The list of CLI arguments which have been passed to the Monkey Wrench.

    Warning:
        The zeroth argument is always the path of the script that is being executed, i.e.
        `<path>/monkey_wrench` in this case.
    """

    # noinspection PyNestedDecorators
    @model_validator(mode="after")
    @classmethod
    def validate_number_of_inputs(cls, instance: Self) -> Self:
        """Ensure that the number of input arguments is correct."""
        if len(cls.cli_args) != 2:
            raise PydanticCustomError(
                "cli_arguments",
                "Expected a single `command-line argument`, but received {n_args}.",
                dict(n_args=len(cls.cli_args) - 1),
            )
        cls.task_filepath = cls.cli_args[1]
        return instance

    # noinspection PyNestedDecorators
    @model_validator(mode="after")
    @classmethod
    def validate_task_filepath_extension(cls, instance: Self) -> Self:
        """Ensure that the task filepath ends in `.yaml` or `.yml`."""
        if not (cls.task_filepath.endswith(".yaml") or cls.task_filepath.endswith(".yml")):
            raise PydanticCustomError(
                "cli_arguments",
                "The task filepath must end in `.yaml` or `.yml`.",
            )
        return instance
