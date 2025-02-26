from typing import Callable, Literal

from pydantic import FilePath, NonNegativeInt, PositiveInt

from monkey_wrench.date_time import DateTimePeriod, FilePathParser
from monkey_wrench.generic import Pattern
from monkey_wrench.input_output import (
    DateTimeDirectory,
    DirectoryVisitor,
    ModelFile,
    TempDirectory,
    copy_files_between_directories,
)
from monkey_wrench.input_output.seviri import output_filename_from_datetime, seviri_extension_context
from monkey_wrench.query import List


class ChimpRetrieval(
    DateTimeDirectory,
    DateTimePeriod,
    DirectoryVisitor,
    ModelFile,
    TempDirectory
):
    """Pydantic model for CHIMP retrievals."""
    device: Literal["cpu", "cuda"] = "cpu"
    sequence_length: NonNegativeInt = 16
    temporal_overlap: NonNegativeInt = 0
    tile_size: PositiveInt = 256
    verbose: bool = True

    def run_in_batches(self) -> None:
        """Perform CHIMP retrievals in batches."""
        files = self.visit()
        with seviri_extension_context() as chimp_cli:
            lst = List(files, FilePathParser)
            indices = lst.query_indices(self.datetime_period)

            batches = lst.generate_k_sized_batches_by_index(
                self.sequence_length,
                index_start=indices[0],
                index_end=indices[-1]
            )

            for batch in batches:
                self.__run_for_single_batch(batch, chimp_cli)

    def run_for_single_batch(self) -> None:
        """Perform a single CHIMP retrieval for a single batch."""
        batch = self.visit()
        with seviri_extension_context() as chimp_cli:
            self.__run_for_single_batch(batch, chimp_cli)

    def __input_filepaths_as_strings(self, batch: list[FilePath]) -> list[str]:
        """Convert paths to strings and ensure each batch includes the same number of items as sequence length."""
        input_filepaths = [str(i) for i in batch]

        if len(input_filepaths) != self.sequence_length:
            raise ValueError(
                f"Expected to receive {self.sequence_length} input files "
                f"but got {len(input_filepaths)} instead!"
            )
        return input_filepaths

    def __run_for_single_batch(self, batch: list[FilePath], retrieve_function: Callable) -> None:
        """Helper function to perform a single CHIMP retrieval for a single batch."""
        with self.temp_dir_context_manager() as tmp_dir:
            input_filepaths = self.__input_filepaths_as_strings(batch)

            retrieve_function(
                self.model_filepath,
                "seviri",
                input_filepaths,
                tmp_dir,
                device=self.device,
                sequence_length=self.sequence_length,
                temporal_overlap=self.temporal_overlap,
                tile_size=self.tile_size,
                verbose=self.verbose
            )

            last_snapshot = FilePathParser.parse(batch[-1])
            datetime_directory = self.create_datetime_directory(last_snapshot)

            copy_files_between_directories(
                tmp_dir,
                datetime_directory,
                Pattern(sub_strings=str(
                    output_filename_from_datetime(last_snapshot))
                )
            )
