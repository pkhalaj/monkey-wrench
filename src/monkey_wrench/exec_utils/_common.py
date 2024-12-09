"""The module which provide the main executable function for the CLI."""

from functools import wraps
from typing import Any, Callable

from loguru import logger
from pydantic import ValidationError

from ._cli_args import parse


def make_error_message(e: Any) -> str:
    """Make a concise error message."""
    msg = e["msg"].lower() if e["msg"] else ""
    loc = e["loc"] if e["loc"] else []
    loc = ".".join([str(i) for i in loc])
    inp = e["input"]

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
                logger.error(f"Validation error {i + 1} - {make_error_message(e)}")

    return wrapper


@pretty_error_logs
def run() -> None:
    """Main entrypoint when invoked from the CLI."""
    for task in parse():
        task.perform()
