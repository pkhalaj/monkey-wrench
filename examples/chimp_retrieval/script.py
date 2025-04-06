from datetime import UTC, datetime

from monkey_wrench.chimp import ChimpRetrieval
from monkey_wrench.date_time import ChimpFilePathParser, DateTimePeriod
from monkey_wrench.input_output import DirectoryVisitor
from monkey_wrench.query import List

model_filepath = "<replace_with_the_full_path_of_the_chimp_model_file>"
parent_output_directory_path = "<replace_with_the_path_of_the_top_level_directory_where_the_files_are_to_be_stored>"
parent_input_directory_path = "<replace_with_the_path_of_the_top_level_directory_where_the_files_are_to_be_visited>"
temp_directory_path = "<replace_with_the_directory_path_where_the_temp_files_are_to_be_stored>"

datetime_period = DateTimePeriod(
    start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
    end_datetime=datetime(2024, 1, 1, tzinfo=UTC)
)

if __name__ == "__main__":
    lst = List(
        DirectoryVisitor(parent_input_directory_path=parent_input_directory_path),
        ChimpFilePathParser.parse
    ).query(
        datetime_period
    )

    ChimpRetrieval(
        device="cpu",
        sequence_length=16,
        temporal_overlap=0,
        tile_size=256,
        verbose=True,
        model_filepath=model_filepath,
        parent_output_directory_path=parent_output_directory_path,
        temp_directory_path=temp_directory_path,
        datetime_format_string=""  # use an empty string to dump the files at the top-level output directory
    ).run_in_batches(lst)
