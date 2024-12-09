from datetime import datetime, timedelta
from pathlib import Path

from monkey_wrench.input_output import write_items_to_txt_file_in_batches
from monkey_wrench.query import EumetsatAPI, EumetsatCollection

filename = Path("seviri_product_ids.txt")

api = EumetsatAPI(
    collection=EumetsatCollection.seviri,
    log_context="Example [Fetch Product IDs]"
)

product_batches = api.query_in_batches(
    start_datetime=datetime(2015, 6, 1),
    end_datetime=datetime(2015, 8, 1),
    batch_interval=timedelta(days=30)
)

write_items_to_txt_file_in_batches(product_batches, filename)
