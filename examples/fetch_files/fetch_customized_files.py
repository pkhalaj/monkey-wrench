from datetime import datetime
from pathlib import Path

from monkey_wrench.query import EumetsatAPI, EumetsatCollection


start = datetime(2021, 1, 1)
end = datetime(2021, 1, 2)
geometry = [  # polygon vertices (lon, lat) of small bounding box in central Sweden
    (14.0, 64.0),
    (16.0, 64.0),
    (16.0, 62.0),
    (14.0, 62.0),
    (14.0, 64.0),
]
nswe = [74.0, 54.0, 6.0, 26.0]  # North, South, West, East bounding box
outpath = Path.cwd()
api = EumetsatAPI(EumetsatCollection.amsu)
results = api.query(start, end, geometry=geometry)
outfiles = api.fetch(results, outpath, bbox=nswe)
print(outfiles)


