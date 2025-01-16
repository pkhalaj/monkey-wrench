"""The module providing common types used in the ``query`` package."""
from enum import Enum
from typing import Generator, TypeVar

from pydantic import BaseModel, validate_call

from monkey_wrench.date_time import Minutes


class CollectionMeta(BaseModel):
    """Named tuple to gather the collection metadata."""
    query_string: str
    """A colon (``:``) delimited string which represents the query string for the collection on the EUMETSAT API.

    Example:
        For SEVIRI we have: ``"EO:EUM:DAT:MSG:HRSEVIRI"``.
    """

    snapshot_minutes: Minutes | None = None
    """The minutes for which we have data in an hour.

    Warning:
        For collections that this does not apply, set the default value, i.e. ``None``.

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


class BoundingBox(BaseModel):
    """Pydantic model for a bounding box.

    Example:
        >>> BoundingBox(north=10, south=20, west=30, east=40)
        north=10 south=20 west=30 east=40

        >>> BoundingBox(10, 20, 30, 40)
        north=10 south=20 west=30 east=40
    """

    north: float
    south: float
    west: float
    east: float

    @validate_call
    def __init__(self, north: float = None, south: float = None, west: float = None, east: float = None):
        kwargs = dict(north=north, south=south, west=west, east=east)
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        super().__init__(**kwargs)

    def serialize(self, as_string: bool = False, delimiter: str = " ") -> list[float] | str:
        """Get the serialized version of the bounding box.

        Args:
            as_string:
                If ``True``, return a string representation of the bounding box.
            delimiter:
                The delimiter to use in the serialized version of the bounding box, if ``as_string`` is ``True``.
                Defaults to a blank space.

        Returns:
            Either a string, or a list of floats as ``[<North>, <South>, <West>, <East>]``.
        """
        lst = [self.north, self.south, self.west, self.east]

        if as_string:
            return delimiter.join([str(i) for i in lst])
        return lst


class Vertex(BaseModel):
    """Pydantic model for a vertex.

    Example:
        >>> Vertex(longitude=10, latitude=20)
        longitude=10 latitude=20

        >>> Vertex(10, 20)
        longitude=10 latitude=20
    """

    longitude: float
    latitude: float

    @validate_call
    def __init__(self, longitude: float = None, latitude: float = None):
        kwargs = dict(longitude=longitude, latitude=latitude)
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**kwargs)

    def serialize(self, as_string: bool = False, delimiter: str = " ") -> list[float] | str:
        """Get the serialized version of the vertex.

        Args:
            as_string:
                If ``True``, return a string representation of the vertex.
            delimiter:
                The delimiter to use in the serialized version of the vertex, if ``as_string`` is ``True``.
                Defaults to a blank space.

        Returns:
            Either a string, or a list of floats as ``[<longitude>, <latitude>]``.
        """
        lst = [self.longitude, self.latitude]

        if as_string:
            return delimiter.join([str(i) for i in lst])
        return lst


class Polygon(BaseModel):
    """The Pydantic model for a polygon.

    Example:
        >>> polygon: Polygon = Polygon(vertices=[
        ...  Vertex(14.0, 64.0),
        ...  Vertex(16.0, 64.0),
        ...  Vertex(16.0, 62.0),
        ...  Vertex(14.0, 62.0),
        ...  Vertex(14.0, 64.0),
        ... ])
    """
    vertices: list[Vertex]

    @validate_call
    def __init__(self, vertices: list[Vertex] = None):
        kwargs = dict(vertices=vertices) if vertices else {}
        super().__init__(**kwargs)

    def serialize(self, as_string: bool = False) -> list[list[float]] | str:
        """Get the serialized version of the polygon.

        Args:
            as_string:
                If ``True``, return a string representation of the polygon.

        Returns:
            Either a string, or a list of vertices, where each vertex is itself a list of floats.
        """
        lst = [v.serialize(as_string=as_string) for v in self.vertices]

        if as_string:
            return f"POLYGON(({','.join(lst)}))"

        return lst


T = TypeVar("T")
Batches = Generator[tuple[T, int], None, None]
"""Type alias for search results in batches.

For each batch there exists a 2-tuple, in which the first element is the returned items and the second element is the
number of returned items in the same batch.
"""
