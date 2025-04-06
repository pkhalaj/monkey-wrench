"""Module to define Pydantic models for tasks related to CHIMP retrievals."""

from typing import Literal

from monkey_wrench.chimp import ChimpRetrieval
from monkey_wrench.date_time import ChimpFilePathParser, DateTimePeriod
from monkey_wrench.input_output import Items
from monkey_wrench.query import List
from monkey_wrench.task.base import Action, Context, TaskBase


class ChimpTaskBase(TaskBase):
    """Pydantic base model for all CHIMP related tasks."""
    context: Literal[Context.chimp]


class ChimpRetrieveSpecifications(ChimpRetrieval, DateTimePeriod):
    """Pydantic base model for the specifications of a retrieve task."""
    items: Items
    """The items to perform the retrieval on which will be further filter by the given datetime period."""


class ChimpRetrieve(ChimpTaskBase):
    """Pydantic model for the CHIMP retrieval task."""
    action: Literal[Action.retrieve]
    specifications: ChimpRetrieveSpecifications

    @TaskBase.log
    def perform(self) -> None:
        """Perform CHIMP retrievals."""
        lst = List(self.specifications.items, ChimpFilePathParser.parse)
        if self.specifications.datetime_period.as_tuple() != (None, None):
            lst = lst.query(self.specifications.datetime_period)
        self.specifications.run_in_batches(lst)


ChimpTask = ChimpRetrieve
