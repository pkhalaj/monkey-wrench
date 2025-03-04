from datetime import UTC, datetime
from pathlib import Path

from monkey_wrench.date_time import ChimpFilePathParser, DateTimePeriod, SeviriIDParser
from monkey_wrench.input_output import DirectoryVisitor, FilesIntegrityValidator
from monkey_wrench.query import List

reference = Path("<replace_with_the_full_path_of_the_text_file_in_which_product_ids_are_stored>")
parent_directory_path = Path("<replace_with_the_path_of_the_top_level_directory_where_the_files_are_to_be_stored>")

datetime_period = DateTimePeriod(
    start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
    end_datetime=datetime(2024, 1, 1, tzinfo=UTC)
)

files_validator = FilesIntegrityValidator(
    nominal_file_size="<replace_with_nominal_size_of_a_single_file_in_bytes_as_an_integer>",
    file_size_relative_tolerance=0.01,
    number_of_processes=20,
    filepath_transform_function=ChimpFilePathParser.parse
)

if __name__ == "__main__":
    files = List(
        DirectoryVisitor(parent_input_directory_path=parent_directory_path).visit(),
        ChimpFilePathParser
    ).query(
        datetime_period
    ).to_python_list()

    reference = List(
        files_validator.get_reference_items(reference),
        SeviriIDParser
    ).query(
        datetime_period
    ).parsed_items.tolist()

    missing, corrupted = files_validator.verify_files(files, reference)

    print({
        "number of files found": len(files),
        "number of reference items ": len(reference),
        "number of missing files": len(missing),
        "corrupted files": corrupted,
    })
