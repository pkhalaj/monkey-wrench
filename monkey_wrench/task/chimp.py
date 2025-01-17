"""Module to define Pydantic models for running CHIMP retrievals."""
from pathlib import Path
from typing import Callable, ClassVar, Literal

from monkey_wrench.date_time import DateTimeRange, FilePathParser
from monkey_wrench.input_output import (
    InputDirectory,
    ModelFile,
    OutputDirectory,
    TempDirectory,
    copy_files_between_directories,
    create_datetime_directory,
    visit_files_in_directory,
)
from monkey_wrench.input_output.seviri import output_filename_from_datetime, seviri_extension_context
from monkey_wrench.query import List
from monkey_wrench.task.base import Action, Context, TaskBase


class Task(TaskBase):
    """Pydantic base model for all CHIMP related tasks."""
    context: Literal[Context.chimp]


class RetrieveSpecifications(DateTimeRange, InputDirectory, ModelFile, OutputDirectory, TempDirectory):
    """Pydantic model for the specifications of CHIMP retrievals."""
    device: Literal["cpu", "cuda"]


class Retrieve(Task):
    """Pydantic model for the CHIMP retrieval task."""
    action: Literal[Action.retrieve]
    specifications: RetrieveSpecifications
    sequence_length: ClassVar[int] = 16

    @TaskBase.log
    def perform(self) -> None:
        """Perform CHIMP retrievals."""
        with seviri_extension_context() as chimp_cli:
            files = visit_files_in_directory(self.specifications.input_directory)
            lst = List(files, FilePathParser)
            indices = lst.query_indices(
                self.specifications.start_datetime,
                self.specifications.end_datetime
            )

            batches = lst.generate_k_sized_batches_by_index(
                Retrieve.sequence_length,
                index_start=indices[0],
                index_end=indices[-1]
            )

            for batch in batches:
                self.run_chimp(chimp_cli, batch)

    def run_chimp(self, retrieve_function: Callable, batch: list[Path]):
        """Run the CHIMP retrieval."""
        input_filenames = [str(i) for i in batch]

        if len(input_filenames) != Retrieve.sequence_length:
            raise ValueError(
                f"Expected to receive {Retrieve.sequence_length} input files but got {len(input_filenames)} instead!"
            )

        retrieve_function(
            self.specifications.model_filename,
            "seviri",
            input_filenames,
            self.specifications.temp_directory,
            device=self.specifications.device,
            sequence_length=Retrieve.sequence_length,
            temporal_overlap=0,
            tile_size=256,
            verbose=1
        )

        datetime_dir = create_datetime_directory(
            FilePathParser.parse(input_filenames[-1]),
            parent=self.specifications.output_directory
        )

        last_retrieved_snapshot = output_filename_from_datetime(FilePathParser.parse(batch[-1]))

        copy_files_between_directories(
            self.specifications.temp_directory,
            datetime_dir,
            pattern=str(last_retrieved_snapshot)
        )

        visit_files_in_directory(
            self.specifications.temp_directory,
            callback=Path.unlink
        )


ChimpTask = Retrieve
