from datetime import datetime
from pathlib import Path

from query import EumetsatCollection

from monkey_wrench.query import EumetsatAPI

output_directory = Path("<replace-with-directory-where-the-files-are-to-be-stored>")
start_datetime = datetime(2021, 1, 1)
end_datetime = datetime(2021, 1, 2)

# North, South, West, and East
bounding_box = [74.0, 54.0, 6.0, 26.0]

# The polygon vertices (lon, lat) of a small bounding box in central Sweden
geometry = [
    (14.0, 64.0),
    (16.0, 64.0),
    (16.0, 62.0),
    (14.0, 62.0),
    (14.0, 64.0),
]

api = EumetsatAPI(EumetsatCollection.amsu)
results = api.query(start_datetime, end_datetime, polygon=geometry)
saved_files = api.fetch_products(results, output_directory, bounding_box=bounding_box)

print(f"Fetch {len(saved_files)} files and store them in {output_directory}.")
