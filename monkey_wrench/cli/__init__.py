"""The package providing functionalities needed for invoking Monkey Wrench from the CLI, i.e. the task runner mode."""

from ._args import CommandLineArguments
from ._common import run

__all__ = [
    "CommandLineArguments",
    "run"
]
