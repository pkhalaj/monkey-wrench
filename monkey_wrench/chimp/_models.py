import tempfile
from pathlib import Path
from typing import Callable, Literal
from uuid import uuid4

from loguru import logger
from pydantic import FilePath, NonNegativeInt, PositiveInt

from monkey_wrench.date_time import ChimpFilePathParser
from monkey_wrench.generic import Pattern
from monkey_wrench.input_output import (
    DateTimeDirectory,
    ModelFile,
    copy_files_between_directories,
)
from monkey_wrench.input_output.seviri import output_filename_from_datetime, seviri_extension_context
from monkey_wrench.query import List


class ChimpRetrieval(
    DateTimeDirectory,
    ModelFile
):
    """Pydantic model for CHIMP retrievals."""
    device: Literal["cpu", "cuda"] = "cpu"
    sequence_length: NonNegativeInt = 16
    temporal_overlap: NonNegativeInt = 0
    tile_size: PositiveInt = 256
    verbose: bool = True

    strict: bool = False
    """Determines whether an exception must be raised if there are missing timestamps. Defaults to ``False``.

    By default, CHIMP is expected to handle missing timestamps if they are not in the beginning or the end of the
    sequence. In such cases, we log a warning. However, if this is set to ``True`` we raise an exception instead.

    Warning:
        It is not 100% guaranteed that a retrieval can always be performed in the absence of some timestamps. There
        might be edge cases that CHIMP cannot handle.
    """

    def run_in_batches(self, lst: List) -> None:
        """Perform CHIMP retrievals in batches."""
        with seviri_extension_context() as chimp_cli:
            batches = lst.generate_k_sized_batches_by_index(self.sequence_length, strict=False)

            for batch in batches:
                self.__run_for_single_batch(batch, chimp_cli)

    def __input_filepaths_as_strings(self, batch: list[FilePath]) -> list[str]:
        """Convert paths to strings and ensure each batch includes the same number of items as sequence length."""
        input_filepaths = [str(i) for i in batch]

        if len(input_filepaths) != self.sequence_length:
            msg = f"Expected to receive {self.sequence_length} input files but got {len(input_filepaths)} instead!"
            msg += f" Batch: {batch}"
            if self.strict:
                raise ValueError(msg)
            logger.warning(msg)

        return input_filepaths

    def __run_for_single_batch(self, batch: list[FilePath], retrieve_function: Callable) -> None:
        """Helper function to perform a single CHIMP retrieval for a single batch."""
        log_id = uuid4()
        with tempfile.TemporaryDirectory(prefix=f"chimp_{log_id}_") as tmp_dir:
            input_filepaths = self.__input_filepaths_as_strings(batch)

            retrieve_function(
                self.model_filepath,
                "seviri",
                input_filepaths,
                tmp_dir,
                device=self.device,
                sequence_length=self.sequence_length,
                temporal_overlap=self.temporal_overlap,
                tile_size=self.tile_size
            )

            last_snapshot = ChimpFilePathParser.parse(batch[-1])
            datetime_directory = self.create_datetime_directory(last_snapshot)

            copied_files = copy_files_between_directories(
                Path(tmp_dir),
                datetime_directory,
                Pattern(
                    sub_strings=str(output_filename_from_datetime(last_snapshot))
                )
            )

            match len(copied_files):
                case 0:
                    logger.error(f"Could not perform a retrieval for {batch}")
                case 1:
                    logger.success("Successfully performed a retrieval.")
                case n:
                    logger.error(f"Expected a single file for the retrieval but copied {n} files. Batch: {batch}")
