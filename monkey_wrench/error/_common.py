"""The module providing the decorator for pretty-printing of error messages."""

from functools import wraps
from typing import Any, Callable

from loguru import logger
from pydantic import ValidationError


def __make_better_error_message(exception: Any) -> str:
    """Make a concise and a better-formatted error message.

    Args:
        exception:
            The given exception instance.

    Returns:
        A string containing the error message with an enhanced format.
    """
    inp, loc, msg = exception["input"], exception["loc"], exception["msg"]
    msg = msg.lower() if msg else ""

    if not loc:
        return msg

    loc = ".".join([str(i) for i in loc])

    return f"{msg} -- `{inp}` of type <{type(inp).__name__}> is invalid for assignment to `{loc}`."


def pretty_error_logs(func: Callable) -> Callable:
    """Decorator to catch and log prettier error messages when running in the task runner mode."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function to catch and log error messages."""
        try:
            return func(*args, **kwargs)
        except ValidationError as err:
            n_errors = len(err.errors())
            logger.error(f"Found {n_errors} validation error{'' if n_errors == 1 else 's'} in total.")
            for i, e in enumerate(err.errors()):
                logger.error(f"Validation error {i + 1} -- {__make_better_error_message(e)}")

    return wrapper
