from datetime import datetime
from pathlib import Path

from chimp import processing

from monkey_wrench.date_time import FilenameParser
from monkey_wrench.input_output import (
    copy_files_between_directories,
    create_datetime_directory,
    seviri,
    visit_files_in_directory,
)
from monkey_wrench.query import List

# Check here!
input_directory = Path("<replace-with-directory-where-the-seviri-files-are-stored>")
output_directory = Path("<replace-with-directory-where-the-chimp-outputs-are-to-be-stored>")
model_filename = Path("<replace-with-full-path-and-filename-of-the-chimp-model-file>")
temp_directory = Path("<replace-with-a-temp-directory>")
device = "cpu"

start_datetime = datetime(2022, 2, 1)
end_datetime = datetime(2022, 2, 10)

sequence_length = 16


def run_chimp(batch: list[Path]):
    input_filenames = [str(i) for i in batch]

    if len(input_filenames) != sequence_length:
        raise ValueError(
            f"Expected to receive {sequence_length} input files but got {len(input_filenames)} instead!"
        )

    processing.cli(
        model_filename,
        "seviri",
        input_filenames,
        str(temp_directory),
        device=device,
        sequence_length=sequence_length,
        temporal_overlap=0,
        tile_size=256,
        verbose=1
    )

    datetime_dir = create_datetime_directory(
        FilenameParser.parse(input_filenames[-1]),
        parent=output_directory
    )

    last_retrieved_snapshot = seviri.output_filename_from_datetime(FilenameParser.parse(batch[-1]))

    copy_files_between_directories(
        temp_directory,
        datetime_dir,
        pattern=str(last_retrieved_snapshot)
    )

    visit_files_in_directory(
        temp_directory,
        callback=Path.unlink
    )


with seviri.seviri_extension_context("seviri"):
    files = visit_files_in_directory(input_directory)
    lst = List(files, FilenameParser)
    indices = lst.query_indices(
        start_datetime,
        end_datetime
    )

    batches = lst.generate_k_sized_batches_by_index(
        sequence_length,
        index_start=indices[0],
        index_end=indices[-1]
    )

    for batch in batches:
        run_chimp(batch)
