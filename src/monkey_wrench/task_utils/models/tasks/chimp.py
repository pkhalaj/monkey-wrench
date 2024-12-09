"""Module to define Pydantic models for running CHIMP retrievals."""

from pathlib import Path
from typing import ClassVar, Literal

from chimp import processing

from monkey_wrench.datetime_utils import FilenameParser
from monkey_wrench.io_utils import (
    collect_files_in_directory,
    copy_files_between_directories,
    create_datetime_directory,
    extension,
)
from monkey_wrench.io_utils.seviri import SEVIRI
from monkey_wrench.query_utils import List
from monkey_wrench.task_utils.models.specifications.datetime import DateTimeRange
from monkey_wrench.task_utils.models.specifications.paths import (
    InputDirectory,
    ModelFile,
    OutputDirectory,
    TempDirectory,
)

from .base import Action, Context, TaskBase


class Task(TaskBase):
    context: Literal[Context.chimp]


class RetrieveSpecifications(DateTimeRange, InputDirectory, ModelFile, OutputDirectory, TempDirectory):
    device: Literal["cpu", "cuda"]
    pass


class Retrieve(Task):
    action: Literal[Action.retrieve]
    specifications: RetrieveSpecifications
    sequence_length: ClassVar[int] = 16

    @TaskBase.log
    def perform(self) -> None:
        """Perform CHIMP retrievals."""
        with extension(SEVIRI, "seviri"):
            files = collect_files_in_directory(self.specifications.input_directory)
            lst = List(files, FilenameParser)
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
                self.run_chimp(batch)

    def run_chimp(self, batch: list[Path]):
        input_filenames = [str(i) for i in batch]

        if len(input_filenames) != Retrieve.sequence_length:
            raise ValueError(
                f"Expected to receive {Retrieve.sequence_length} input files but got {len(input_filenames)} instead!"
            )

        processing.cli(
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
            FilenameParser.parse(input_filenames[-1]),
            parent=self.specifications.output_directory
        )

        copy_files_between_directories(
            self.specifications.temp_directory,
            datetime_dir,
            pattern=batch[-1].stem
        )

        collect_files_in_directory(
            self.specifications.temp_directory,
            callback=Path.unlink
        )


ChimpTask = Retrieve
