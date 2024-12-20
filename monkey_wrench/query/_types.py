from typing import Any, Generator

BoundingBox = tuple[float, float, float, float]
"""Type alias for a 4-tuple (of floats) determining the bounds for (North, South, West, East).

Example:
    >>> from monkey_wrench.query import BoundingBox
    >>> bounding_box: BoundingBox  = [74.0, 54.0, 6.0, 26.0]
"""

Polygon = list[tuple[float, float]]
"""Type alias for a list of 2-tuples (of floats) to determine the vertices of a polygon.

Example:
    >>> from monkey_wrench.query import Polygon
    >>> polygon: Polygon = [
    ...  (14.0, 64.0),
    ...  (16.0, 64.0),
    ...  (16.0, 62.0),
    ...  (14.0, 62.0),
    ...  (14.0, 64.0)
    ... ]
"""

Results = Generator[tuple[Any, int], None, None]
"""Type alias for search results in batches.

For each batch there exists a 2-tuple, in which the first element is the returned items and the second element is the
number of the items.
"""
