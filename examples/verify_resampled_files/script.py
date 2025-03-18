from datetime import UTC, datetime
from pathlib import Path

from monkey_wrench.date_time import ChimpFilePathParser, DateTimePeriod, SeviriIDParser
from monkey_wrench.generic import StringTransformation
from monkey_wrench.input_output import DirectoryVisitor, FilesIntegrityValidator, Reader
from monkey_wrench.query import List

nominal_file_size = "<replace_with_nominal_size_of_a_single_file_in_bytes_as_an_integer>",
input_filepath = "<replace_with_the_full_path_of_the_text_file_in_which_product_ids_are_stored>",
parent_input_directory_path = Path(
    "<replace_with_the_path_of_the_top_level_directory_where_the_files_are_to_be_stored>"
)
datetime_period = DateTimePeriod(
    start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
    end_datetime=datetime(2024, 1, 1, tzinfo=UTC)
)

if __name__ == "__main__":
    reference = Reader(
        input_filepath=input_filepath,
        post_reading_transformation=StringTransformation(
            transform_function=SeviriIDParser.parse
        )
    ).read()

    files = List(
        DirectoryVisitor(parent_input_directory_path=parent_input_directory_path).visit(),
        ChimpFilePathParser.parse
    ).query(
        datetime_period
    ).to_python_list()

    reference = List(
        reference,
    ).query(
        datetime_period
    ).parsed_items.tolist()

    files_validator = FilesIntegrityValidator(
        filepaths=files,
        nominal_file_size=nominal_file_size,
        file_size_relative_tolerance=0.01,
        number_of_processes=20,
        reference=reference,
        filepath_transform_function=ChimpFilePathParser.parse
    )

    missing, corrupted = files_validator.verify_files()

    print({
        "number of files found": len(files),
        "number of reference items ": len(reference),
        "number of missing files": len(missing),
        "corrupted files": corrupted,
    })
