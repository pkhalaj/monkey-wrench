"""Module to define Pydantic models for tasks related to product files."""

from typing import Literal

from pydantic import NonNegativeInt

from monkey_wrench.date_time import DateTimePeriod, FilePathParser, SeviriIDParser
from monkey_wrench.input_output import DirectoryVisitor, FilesIntegrityValidator, Reader, TempDirectory
from monkey_wrench.input_output.seviri import Resampler
from monkey_wrench.process import MultiProcess
from monkey_wrench.query import List
from monkey_wrench.task.base import Action, Context, TaskBase


class Task(TaskBase):
    """Pydantic base model for tasks related to product files."""
    context: Literal[Context.product_files]


class VerifySpecifications(DateTimePeriod, DirectoryVisitor, FilesIntegrityValidator, Reader):
    """Pydantic model for the specifications of a verification task."""
    pass


class FetchSpecifications(
    DateTimePeriod,
    MultiProcess,
    Resampler,
    Reader,
    TempDirectory
):
    """Pydantic model for the specifications of a fetch task."""
    pass


class Verify(Task):
    """Pydantic model for the verification task."""
    action: Literal[Action.verify]
    specifications: VerifySpecifications

    @TaskBase.log
    def perform(self) -> dict[str, NonNegativeInt]:
        """Verify the product files using the reference."""
        files = List(
            self.specifications.visit(),
            FilePathParser
        ).query(
            self.specifications.datetime_period
        ).to_python_list()

        self.specifications.reference = List(
            self.specifications.reference,
            SeviriIDParser
        ).query(
            self.specifications.datetime_period
        ).parsed_items.tolist()

        self.specifications.transform_function = FilePathParser.parse
        missing, corrupted = self.specifications.verify(files)

        return {
            "number of files found": len(files),
            "number of reference items": len(self.specifications.reference),
            "number of missing files": len(missing),
            "number of corrupted files": len(corrupted),
        }


class Fetch(Task):
    """Pydantic model for the fetch task."""
    action: Literal[Action.fetch]
    specifications: FetchSpecifications

    @TaskBase.log
    def perform(self) -> None:
        """Fetch the product files."""
        product_ids = List(
            self.specifications.read(),
            SeviriIDParser
        ).query(
            self.specifications.datetime_period
        )
        for product_id in product_ids:
            self.specifications.create(SeviriIDParser.parse(product_id))
        with TempDirectory(temp_directory=self.specifications.temp_directory).context():
            self.specifications.run(self.specifications.resample, product_ids.to_python_list())


FilesTask = Fetch | Verify
