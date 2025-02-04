"""The Pydantic model to parse CLI arguments."""

import sys
from typing import ClassVar, Self

from pydantic import model_validator
from pydantic_core import PydanticCustomError

from monkey_wrench.generic import Model
from monkey_wrench.input_output import InputFile


class CommandLineArguments(Model):
    """Pydantic model to validate CLI arguments.

    It reads the CLI arguments from `sys.argv`_, where ``sys.argv[0]`` is the path of the script which is being
    executed, i.e. ``monkey-wrench`` in this case. As a result, the actual arguments are ``sys.argv[1:]``.

    .. _sys.argv: https://docs.python.org/3/library/sys.html#sys.argv
    """

    task_filepath: ClassVar[InputFile]
    """The path of the task file, which must point to an existing valid YAML file."""

    # noinspection PyNestedDecorators
    @model_validator(mode="after")
    @classmethod
    def validate_number_of_inputs(cls, instance: Self) -> Self:
        """Ensure that the number of input arguments is correct."""
        if len(sys.argv) != 2:
            raise PydanticCustomError(
                "cli_arguments",
                "Expected a single command-line argument, but received {n_args} arguments.",
                dict(n_args=len(sys.argv) - 1),
            )
        return instance

    # noinspection PyNestedDecorators
    @model_validator(mode="after")
    @classmethod
    def validate_task_filepath_existence(cls, instance: Self) -> Self:
        """Check that the task file exists and convert its path to an absolute path."""
        cls.task_filepath = InputFile(input_filename=sys.argv[1])
        return instance
