"""Module to define Pydantic models for tasks related to CHIMP retrievals."""

from typing import Literal

from monkey_wrench.chimp import ChimpRetrieval
from monkey_wrench.task.base import Action, Context, TaskBase


class ChimpTaskBase(TaskBase):
    """Pydantic base model for all CHIMP related tasks."""
    context: Literal[Context.chimp]


ChimpRetrieveSpecifications = ChimpRetrieval


class ChimpRetrieve(ChimpTaskBase):
    """Pydantic model for the CHIMP retrieval task."""
    action: Literal[Action.retrieve]
    specifications: ChimpRetrieveSpecifications

    @TaskBase.log
    def perform(self) -> None:
        """Perform CHIMP retrievals."""
        self.specifications.run_in_batches()


ChimpTask = ChimpRetrieve
