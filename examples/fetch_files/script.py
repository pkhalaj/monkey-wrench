from datetime import datetime
from pathlib import Path

from monkey_wrench.datetime_utils import SeviriIDParser
from monkey_wrench.io_utils import read_items_from_txt_file, seviri
from monkey_wrench.process_utils import run_multiple_processes
from monkey_wrench.query_utils import EumetsatAPI, List

# Check here!
product_ids_filename = Path("<replace-with-full-path-and-filename-of-the-text-file-in-which-product-ids-are-stored>")
files_directory = Path("<replace-with-directory-where-the-files-are-to-be-stored>")

start_datetime = datetime(2022, 1, 1)
end_datetime = datetime(2024, 1, 1)

product_ids = List(
    read_items_from_txt_file(product_ids_filename),
    SeviriIDParser
).query(
    start_datetime,
    end_datetime
)


def fetch(product_id):
    """Fetch and resample the file with the given product ID."""
    api = EumetsatAPI()
    fs_file = api.open_seviri_native_file_remotely(product_id, cache="filecache")
    seviri.resample_seviri_native_file(
        fs_file,
        files_directory,
        seviri.input_filename_from_product_id
    )


run_multiple_processes(fetch, product_ids, number_of_processes=2)
