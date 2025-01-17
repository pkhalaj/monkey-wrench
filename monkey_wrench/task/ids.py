"""The module providing Pydantic models for tasks related to product IDs."""

from typing import Literal

from pydantic import NonNegativeInt

from monkey_wrench.date_time import DateTimeRangeInBatches
from monkey_wrench.input_output import OutputFile, write_items_to_txt_file_in_batches
from monkey_wrench.query import EumetsatAPI
from monkey_wrench.task.base import Action, Context, TaskBase


class Task(TaskBase):
    """Pydantic base model for tasks related to product IDs."""
    context: Literal[Context.product_ids]


class FetchSpecifications(DateTimeRangeInBatches, OutputFile):
    """Pydantic base model for the specifications of a fetch task."""
    pass


class Fetch(Task):
    """Pydantic base model for the fetch task."""
    action: Literal[Action.fetch]
    specifications: FetchSpecifications

    @TaskBase.log
    def perform(self) -> dict[str, NonNegativeInt]:
        """Fetch the product IDs."""
        api = EumetsatAPI()

        product_batches = api.query_in_batches(
            start_datetime=self.specifications.start_datetime,
            end_datetime=self.specifications.end_datetime,
            batch_interval=self.specifications.batch_interval
        )
        number_of_items = write_items_to_txt_file_in_batches(
            product_batches,
            self.specifications.output_filename
        )

        return {
            "number of items successfully fetched and written to the file": number_of_items,
        }


IdsTask = Fetch
