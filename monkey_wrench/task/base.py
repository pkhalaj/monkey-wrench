"""The module providing base models for tasks."""

from enum import Enum
from functools import wraps
from typing import Any, Callable
from uuid import uuid4

from loguru import logger
from pydantic import BaseModel, InstanceOf, PositiveInt

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


def _fold_collections(
        specifications: Specifications,
        folding_threshold: PositiveInt = 10,
        number_of_items_to_show_at_each_end: PositiveInt = 2,
) -> dict:
    """Fold the collections inside the given specifications if they have too many items.

    This helps with better log messages.
    """
    n = number_of_items_to_show_at_each_end

    def _aux(v):
        if isinstance(v, (list, set, tuple)) and len(v) > folding_threshold:
            _tmp = list(v)
            return [*_tmp[:n], "...", *_tmp[-n:]]
        return v

    return {k: _aux(v) for k, v in specifications.model_dump().items()}


class TaskBase(BaseModel, extra="forbid", arbitrary_types_allowed=True):
    """Pydantic base model for a task."""
    verbose: bool = False
    """Whether the long collections must be folded or not."""
    context: Context
    action: Action
    specifications: type[Specifications]

    @staticmethod
    def log(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        """Decorator to log the details of the given task as well as the returned result."""

        @wraps(func)
        def wrapper(self: InstanceOf[TaskBase]) -> dict[str, Any] | None:
            """Wrapper function to perform the logging first and the task afterward."""
            spec = self.specifications if self.verbose else _fold_collections(self.specifications)
            # The ID helps us to quickly find all log messages corresponding to a single task.
            log_id = uuid4()
            logger.info(
                f"Performing task `{self.context.value}.{self.action.value}` "
                f"with specifications `{spec}` -- ID: `{log_id}`"
            )
            outs = func(self)
            if outs:
                logger.info(f"Retrieved results for task `{log_id}`: `{outs}`")
            return outs

        return wrapper

    def perform(self) -> dict[str, Any] | None:
        """Perform the action using the given arguments."""
        raise NotImplementedError()
