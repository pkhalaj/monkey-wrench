"""Module to define base models."""
from enum import Enum
from functools import wraps
from typing import Any, Callable
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel

from monkey_wrench.task_utils.models.specifications.base import Specifications


class Context(str, Enum):
    """Enum for all possible task contexts."""
    product_ids = "ids"
    product_files = "files"


class Action(str, Enum):
    """Enum for all possible task actions."""
    fetch = "fetch"
    verify = "verify"


class TaskBase(BaseModel, extra="forbid", arbitrary_types_allowed=True):
    """Pydantic base model for a task."""
    context: Context
    action: Action
    specifications: Specifications

    @staticmethod
    def log(func: Callable) -> Callable:
        """Decorator to log the details of the given task as well as the returned result."""

        @wraps(func)
        def wrapper(self, *args, **kwargs) -> dict[str, Any] | None:
            """Wrapper function to perform tha logging first and the task afterward."""
            # The ID helps us to quickly find all log messages corresponding to a single task.
            log_id = uuid4()
            logger.info(
                f"Performing task `{self.action.value}` `{log_id}` for `{self.context.value}` "
                f"with specifications `{self.specifications}`"
            )
            outs = func(self, *args, **kwargs)
            if outs:
                logger.info(f"Retrieved results for task {log_id}: {outs}")
            return outs

        return wrapper

    def perform(self, *args, **kwargs) -> dict[str, Any] | None:
        """Perform the action using the given arguments."""
        raise NotImplementedError()
