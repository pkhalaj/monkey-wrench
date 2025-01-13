"""The module providing common types used in the ``query`` package."""

from enum import Enum
from typing import Generator, TypeVar

from pydantic import BaseModel

from monkey_wrench.date_time import Minutes


class CollectionMeta(BaseModel):
    """Named tuple to gather the collection metadata."""
    query_string: str
    """A colon (:) delimited string which represents the query string for the collection on the EUMETSAT API.

    Example:
        For SEVIRI we have: ``"EO:EUM:DAT:MSG:HRSEVIRI"``.
    """

    snapshot_minutes: Minutes | None = None
    """The minutes for which we have data in an hour.

    Example:
        For SEVIRI we have one snapshot per ``15`` minutes, starting from the 12th minute. As a result, we have
        ``[12, 27, 42, 57]`` for SEVIRI snapshots in an hour.
    """


class EumetsatCollection(Enum):
    """Enum class that defines the collections for the EUMETSAT datastore."""
    amsu = CollectionMeta(query_string="EO:EUM:DAT:METOP:AMSUL1")
    avhrr = CollectionMeta(query_string="EO:EUM:DAT:METOP:AVHRRL1")
    mhs = CollectionMeta(query_string="EO:EUM:DAT:METOP:MHSL1")
    seviri = CollectionMeta(query_string="EO:EUM:DAT:MSG:HRSEVIRI", snapshot_minutes=[12, 27, 42, 57])


BoundingBox = tuple[float, float, float, float]
"""Type alias for a 4-tuple of floats determining the bounds for (North, South, West, East).

Example:
    >>> from monkey_wrench.query import BoundingBox
    >>>
    >>> bounding_box: BoundingBox  = [74.0, 54.0, 6.0, 26.0]
"""


class Polygon(BaseModel):
    """The Pydantic model for a polygon.

    Example:
        >>> from monkey_wrench.query import Polygon
        >>>
        >>> polygon = Polygon(vertices=[
        ...  (14.0, 64.0),
        ...  (16.0, 64.0),
        ...  (16.0, 62.0),
        ...  (14.0, 62.0),
        ...  (14.0, 64.0)
        ... ])
    """
    vertices: list[tuple[float, float]]

    def __str__(self) -> str:
        """Convert the given polygon to a string representation which is expected by the API."""
        coordinates_str = ",".join([f"{lon} {lat}" for lon, lat in self.vertices])
        return f"POLYGON(({coordinates_str}))"


T = TypeVar("T")
Batches = Generator[tuple[T, int], None, None]
"""Type alias for search results in batches.

For each batch there exists a 2-tuple, in which the first element is the returned items and the second element is the
number of returned items in the same batch.
"""
