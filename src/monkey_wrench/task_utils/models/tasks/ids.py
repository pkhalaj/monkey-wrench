"""Module to define Pydantic models for product IDs tasks."""

from typing import Literal

from pydantic import NonNegativeInt

from monkey_wrench import io_utils
from monkey_wrench.query_utils import EumetsatAPI
from monkey_wrench.task_utils.models.specifications.datetime import DateTimeRangeInBatches
from monkey_wrench.task_utils.models.specifications.paths import OutputFile

from .base import Action, Context, TaskBase


class Task(TaskBase):
    context: Literal[Context.product_ids]


class FetchSpecifications(DateTimeRangeInBatches, OutputFile):
    pass


class Fetch(Task):
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
        n = io_utils.write_items_to_txt_file_in_batches(product_batches, self.specifications.output_filename)
        return {
            "number of items successfully fetched and written to the file": n,
        }


IdsTask = Fetch
