"""Module to define Pydantic models for running CHIMP retrievals."""

from pathlib import Path
from typing import Callable, Literal

from pydantic import NonNegativeInt, PositiveInt

from monkey_wrench.date_time import DateTimePeriod, FilePathParser
from monkey_wrench.generic import Pattern
from monkey_wrench.input_output import (
    DateTimeDirectory,
    DirectoryVisitor,
    ModelFile,
    OutputDirectory,
    TempDirectory,
    copy_files_between_directories,
)
from monkey_wrench.input_output.seviri import output_filename_from_datetime, seviri_extension_context
from monkey_wrench.query import List
from monkey_wrench.task.base import Action, Context, TaskBase


class Task(TaskBase):
    """Pydantic base model for all CHIMP related tasks."""
    context: Literal[Context.chimp]


class RetrieveSpecifications(DateTimePeriod, DirectoryVisitor, ModelFile, OutputDirectory, TempDirectory):
    """Pydantic model for the specifications of CHIMP retrievals."""
    device: Literal["cpu", "cuda"] = "cpu"
    sequence_length: NonNegativeInt = 16
    temporal_overlap: NonNegativeInt = 0
    tile_size: PositiveInt = 256
    verbose: PositiveInt = 1


class Retrieve(Task):
    """Pydantic model for the CHIMP retrieval task."""
    action: Literal[Action.retrieve]
    specifications: RetrieveSpecifications

    @TaskBase.log
    def perform(self) -> None:
        """Perform CHIMP retrievals."""
        with seviri_extension_context() as chimp_cli:
            files = self.specifications.visit()
            lst = List(files, FilePathParser)
            indices = lst.query_indices(self.specifications.datetime_period)

            batches = lst.generate_k_sized_batches_by_index(
                self.specifications.sequence_length,
                index_start=indices[0],
                index_end=indices[-1]
            )

            for batch in batches:
                self.run_chimp(chimp_cli, batch)

    def __filepaths_as_strings(self, batch):
        input_filepaths = [str(i) for i in batch]

        if len(input_filepaths) != self.specifications.sequence_length:
            raise ValueError(
                f"Expected to receive {self.specifications.sequence_length} input files "
                f"but got {len(input_filepaths)} instead!"
            )
        return input_filepaths

    def run_chimp(self, retrieve_function: Callable, batch: list[Path]):
        """Run the CHIMP retrieval."""
        input_filepaths = self.__filepaths_as_strings(batch)

        retrieve_function(
            self.specifications.model_filepath,
            "seviri",
            input_filepaths,
            self.specifications.temporary_directory,
            device=self.specifications.device,
            sequence_length=self.specifications.sequence_length,
            temporal_overlap=self.specifications.temporal_overlap,
            tile_size=self.specifications.tile_size,
            verbose=self.specifications.verbose
        )

        last_retrieved_snapshot = str(output_filename_from_datetime(FilePathParser.parse(batch[-1])))

        datetime_directory = DateTimeDirectory(
            parent_directory=self.specifications.output_directory
        ).create_datetime_directory(
            FilePathParser.parse(input_filepaths[-1])
        )

        copy_files_between_directories(
            self.specifications.temporary_directory,
            datetime_directory,
            Pattern(sub_strings=last_retrieved_snapshot)
        )

        DirectoryVisitor(parent_directory=self.specifications.temporary_directory, visitor_callback=Path.unlink).visit()


ChimpTask = Retrieve
