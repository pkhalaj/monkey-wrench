"""The module providing Pydantic models for tasks related to product IDs."""

from typing import Literal

from pydantic import NonNegativeInt

from monkey_wrench.date_time import DateTimeRangeInBatches
from monkey_wrench.input_output import Writer
from monkey_wrench.query import EumetsatQuery
from monkey_wrench.task.base import Action, Context, TaskBase


class Task(TaskBase):
    """Pydantic base model for tasks related to product IDs."""
    context: Literal[Context.product_ids]


class FetchSpecifications(DateTimeRangeInBatches, Writer):
    """Pydantic base model for the specifications of a fetch task."""
    pass


class Fetch(Task):
    """Pydantic base model for the fetch task."""
    action: Literal[Action.fetch]
    specifications: FetchSpecifications

    @TaskBase.log
    def perform(self) -> dict[str, NonNegativeInt]:
        """Fetch the product IDs."""
        product_batches = EumetsatQuery().query_in_batches(self.specifications.datetime_range_in_batches)
        number_of_items = self.specifications.write_in_batches(product_batches)

        return {
            "number of items successfully fetched and written to the file": number_of_items,
        }


IdsTask = Fetch
