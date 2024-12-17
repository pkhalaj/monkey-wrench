"""The module providing the main executable function for the CLI."""

from functools import wraps
from typing import Any, Callable

from loguru import logger
from pydantic import ValidationError

from ._args import parse


def _make_better_error_message(exception: Any) -> str:
    """Make a concise and prettier error message.

    Args:
        exception:
            The given exception instance.

    Returns:
        A string containing the aesthetically enhanced error message.
    """
    msg = exception["msg"].lower() if exception["msg"] else ""
    loc = exception["loc"] if exception["loc"] else []
    loc = ".".join([str(i) for i in loc])
    inp = exception["input"]

    if not loc:
        return msg

    return f"{msg} - '{inp}' of type {type(inp)} is not valid for assignment to '{loc}'."


def pretty_error_logs(func: Callable) -> Callable:
    """Decorator to catch and log prettier error messages when running in the task runner mode."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function to catch and log error messages."""
        try:
            return func(*args, **kwargs)
        except ValidationError as err:
            logger.error(f"Found {len(err.errors())} validation errors.")
            for i, e in enumerate(err.errors()):
                logger.error(f"Validation error {i + 1} - {_make_better_error_message(e)}")

    return wrapper


@pretty_error_logs
def run() -> None:
    """The main entrypoint, when `Monkey Wrench` is invoked from the CLI."""
    for task in parse():
        task.perform()
