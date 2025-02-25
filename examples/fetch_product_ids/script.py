from datetime import UTC, datetime, timedelta
from pathlib import Path

from monkey_wrench.date_time import DateTimeRangeInBatches
from monkey_wrench.input_output import Writer
from monkey_wrench.query import EumetsatQuery

output_filepath = Path("<replace_with_the_full_path_of_the_text_file_in_which_product_ids_are_to_be_stored>")

writer = Writer(output_filepath=output_filepath)
datetime_range_in_batches = DateTimeRangeInBatches(
    start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
    end_datetime=datetime(2024, 1, 1, tzinfo=UTC),
    batch_interval=timedelta(days=30)
)

if __name__ == "__main__":
    product_batches = EumetsatQuery().query_in_batches(datetime_range_in_batches)
    number_of_items = writer.write_in_batches(product_batches)
    print("number of items successfully fetched and written to the file: ", number_of_items)
