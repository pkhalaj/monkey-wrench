"""The module to provide main functions to parse CLI arguments."""

import sys
from typing import Any, ClassVar, Generator

from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError

from monkey_wrench.task import Task, read_tasks_from_file


class CommandLineArguments(BaseModel):
    """Pydantic model to validate CLI arguments."""
    filename: ClassVar[str] = ""
    args: list[str]

    # noinspection PyNestedDecorators
    @model_validator(mode="after")
    @classmethod
    def validate_number_of_inputs(cls, v: Any) -> Any:
        """Validate the number of input arguments."""
        if len(v.args) != 2:
            raise PydanticCustomError(
                "cli_arguments",
                "Expected a single `command-line argument`, but received {n_args}.",
                dict(n_args=len(v.args) - 1),
            )
        cls.filename = v.args[1]
        return v


def parse() -> Generator[Task, None, None]:
    """Parse CLI arguments and a return the corresponding task(s)."""
    parsed_args = CommandLineArguments(args=sys.argv)
    yield from read_tasks_from_file(parsed_args.filename)
