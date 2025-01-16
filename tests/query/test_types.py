import pytest
from pydantic import ValidationError

from monkey_wrench.query import BoundingBox, Polygon, Vertex

# ======================================================
### Tests for Vertex()

@pytest.mark.parametrize("vertex", [
    Vertex(10.0, 12.3),
    Vertex(longitude=10.0, latitude=12.3)
])
@pytest.mark.parametrize(("expected", "kwargs"), [
    ([10.0, 12.3], {}),
    ("10.0 12.3", dict(as_string=True)),
    ("10.0,,12.3", dict(as_string=True, delimiter=",,")),
])
def test_Vertex(vertex, expected, kwargs):
    assert expected == vertex.serialize(**kwargs)


@pytest.mark.parametrize("args", [
    [],
    [10],
    [10, 20, 30]
])
@pytest.mark.parametrize("kwargs", [
    {},
    {"longitude": 10.0},
    {"longitude": 10.0, "latitude": 12.3, "z": 0.0}
])
def test_Vertex_raise(args, kwargs):
    with pytest.raises(ValidationError):
        Vertex(*args, **kwargs)


# ======================================================
### Tests for BoundingBox()

@pytest.mark.parametrize("bounding_box", [
    BoundingBox(10.0, 12.3, 0.0, 15.0),
    BoundingBox(north=10.0, south=12.3, west=0.0, east=15.0),
])
@pytest.mark.parametrize(("expected", "kwargs"), [
    ([10.0, 12.3, 0.0, 15.0], {}),
    ("10.0 12.3 0.0 15.0", dict(as_string=True)),
    ("10.0,,12.3,,0.0,,15.0", dict(as_string=True, delimiter=",,")),
])
def test_BoundingBox(bounding_box, expected, kwargs):
    assert expected == bounding_box.serialize(**kwargs)


@pytest.mark.parametrize("args", [
    [],
    [10],
    [10, 20, 30, 40, 50]
])
@pytest.mark.parametrize("kwargs", [
    {},
    {"north": 10.0},
    {"north": 10.0, "south": 12.3, "west": 0.0, "east": 15.0, "z": 0.0},
])
def test_BoundingBox_raise(args, kwargs):
    with pytest.raises(ValidationError):
        BoundingBox(*args, **kwargs)


# ======================================================
### Tests for Polygon()

@pytest.mark.parametrize("polygon", [
    Polygon([Vertex(10.0, 12.3), Vertex(0.0, 15.0)]),
    Polygon(vertices=[Vertex(10.0, 12.3), Vertex(0.0, 15.0)]),
])
@pytest.mark.parametrize(("expected", "kwargs"), [
    ([[10.0, 12.3], [0.0, 15.0]], {}),
    ("POLYGON((10.0 12.3,0.0 15.0))", dict(as_string=True)),
])
def test_Polygon(polygon, expected, kwargs):
    assert expected == polygon.serialize(**kwargs)


@pytest.mark.parametrize("args", [
    [],
    [[10, 12.3]]
])
@pytest.mark.parametrize("kwargs", [
    {},
    {"vertices": [Vertex(10.0, 12.3)], "z": 0.0}
])
def test_Polygon_raise(args, kwargs):
    with pytest.raises(ValidationError):
        Polygon(*args, **kwargs)
