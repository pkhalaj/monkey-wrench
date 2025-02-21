import sys
from typing import Any, ClassVar

from pydantic import model_validator
from pydantic_core import PydanticCustomError

from monkey_wrench.generic import Model
from monkey_wrench.input_output import ExistingFilePath, ExistingInputFile


class CommandLineArguments(Model):
    """Pydantic model to validate CLI arguments.

    It reads the CLI arguments from `sys.argv`_, where ``sys.argv[0]`` is the path of the script which is being
    executed, i.e. ``monkey-wrench`` in this case. As a result, the actual arguments are ``sys.argv[1:]``.

    .. _sys.argv: https://docs.python.org/3/library/sys.html#sys.argv
    """

    task_file_path: ClassVar[ExistingFilePath]
    """The path to the task file, which must be an existing valid YAML file."""

    @model_validator(mode="before")
    def validate_task_filepath_existence(cls, data: Any) -> Any:
        """Check that the task file exists and assign it to the class variable."""
        CommandLineArguments.task_file_path = ExistingInputFile(input_filepath=sys.argv[1]).input_filepath
        return data

    @model_validator(mode="before")
    def validate_number_of_inputs(cls, data: Any) -> Any:
        """Ensure that the number of input arguments is correct."""
        if len(sys.argv) != 2:
            raise PydanticCustomError(
                "cli_arguments",
                "Expected a single command-line argument, but received {n_args} arguments.",
                dict(n_args=len(sys.argv) - 1),
            )
        return data
