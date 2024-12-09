from datetime import datetime
from pathlib import Path

from monkey_wrench.datetime_utils import FilenameParser, SeviriIDParser
from monkey_wrench.io_utils import collect_files_in_directory, compare_files_against_reference, read_items_from_txt_file
from monkey_wrench.query_utils import List

# Check here!
product_ids_filename = Path("<replace-with-full-path-and-filename-of-the-text-file-in-which-product-ids-are-stored>")
input_directory = Path("<replace-with-directory-where-the-files-are-stored>")

start_datetime = datetime(2022, 1, 1)
end_datetime = datetime(2024, 1, 1)

product_ids = List(
    read_items_from_txt_file(product_ids_filename),
    SeviriIDParser
).query(
    start_datetime,
    end_datetime
)
expected_datetime_instances = [SeviriIDParser.parse(i) for i in product_ids]

collected_files = List(
    collect_files_in_directory(input_directory),
    FilenameParser
).query(
    start_datetime,
    end_datetime
)

missing, corrupted = compare_files_against_reference(
    collected_files,
    reference_list=expected_datetime_instances,
    transform_function=FilenameParser.parse,
    nominal_size=0,  # replace 0 with the nominal size of a single file in bytes (positive integer!)
    tolerance=0.01
)

print({
    "number of files found": len(collected_files),
    "number of reference items ": len(expected_datetime_instances),
    "number of missing files": len(missing),
    "number of corrupted files": len(corrupted),
})
