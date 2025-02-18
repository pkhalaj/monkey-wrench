"""The module providing base models for tasks."""

from enum import Enum
from functools import wraps
from typing import Any, Callable
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel

from monkey_wrench.generic import Model

Specifications = Model


class Context(str, Enum):
    """Enum for all possible task contexts."""
    product_ids = "ids"
    product_files = "files"
    chimp = "chimp"


class Action(str, Enum):
    """Enum for all possible task actions."""
    fetch = "fetch"
    verify = "verify"
    retrieve = "retrieve"


class TaskBase(BaseModel, extra="forbid", arbitrary_types_allowed=True):
    """Pydantic base model for a task."""
    context: Context
    action: Action
    specifications: type[Specifications]

    @staticmethod
    def log(func: Callable) -> Callable:
        """Decorator to log the details of the given task as well as the returned result."""

        @wraps(func)
        def wrapper(self) -> dict[str, Any] | None:
            """Wrapper function to perform tha logging first and the task afterward."""
            # The ID helps us to quickly find all log messages corresponding to a single task.
            log_id = uuid4()
            logger.info(
                f"Performing task `{self.context.value}.{self.action.value}` "
                f"with specifications `{self.specifications}` -- ID: `{log_id}`"
            )
            outs = func(self)
            if outs:
                logger.info(f"Retrieved results for task `{log_id}`: `{outs}`")
            return outs

        return wrapper

    def perform(self) -> dict[str, Any] | None:
        """Perform the action using the given arguments."""
        raise NotImplementedError()
