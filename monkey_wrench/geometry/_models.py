from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, FilePath, field_validator, validate_call
from pyresample import AreaDefinition, area_config, load_area

from monkey_wrench.generic import Model
from monkey_wrench.input_output._types import AbsolutePath


class Area(Model):
    area: AbsolutePath[FilePath] | dict[str, Any] | AreaDefinition
    """A filepath, a dictionary, or an object of type AreaDefinition which holds the area information for resampling."""

    @field_validator("area", mode="after")
    def validate_and_load_area(
            cls, area: AbsolutePath[FilePath] | dict[str, Any] | AreaDefinition
    ) -> AreaDefinition | None:
        match area:
            case AreaDefinition():
                return area
            case dict():
                if not area:
                    raise ValueError("The area dictionary cannot be empty.")
                yaml_string = yaml.safe_dump(area)
                return area_config.load_area_from_string(yaml_string)
            case Path():
                return load_area(area)


class BoundingBox(BaseModel):
    """Pydantic model for a bounding box.

    Example:
        >>> BoundingBox(north=10, south=20, west=30, east=40)
        BoundingBox(north=10.0, south=20.0, west=30.0, east=40.0)

        >>> BoundingBox(10, 20, 30, 40)
        BoundingBox(north=10.0, south=20.0, west=30.0, east=40.0)
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
        Vertex(longitude=10.0, latitude=20.0)

        >>> Vertex(10, 20)
        Vertex(longitude=10.0, latitude=20.0)
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
