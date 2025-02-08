from pathlib import Path

import pytest
from pydantic import ValidationError
from pyresample import AreaDefinition, load_area

from monkey_wrench.geometry import Area, BoundingBox, Polygon, Vertex
from tests.utils import make_yaml_file

# ======================================================
### Tests for Area()

def get_area_definition():
    return dict(
        CHIMP_NORDIC_4=dict(
            description="CHIMP region of interest over the nordic countries",
            projection=dict(
                proj="stere",
                lat_0=90,
                lat_ts=60,
                lon_0=14,
                x_0=0,
                y_0=0,
                datum="WGS84",
                no_defs=None,
                type="crs"),
            shape=dict(
                height=564,
                width=452
            ),
            area_extent=dict(
                lower_left_xy=[-745322.8983833211, -3996217.269197446],
                upper_right_xy=[1062901.0232376591, -1747948.2287755085],
                units="m"
            )
        )
    )


def make_area_file(path: Path):
    return make_yaml_file(path / Path("chimp_nordic_4.yml"), get_area_definition())


@pytest.mark.parametrize("area_factory", [
    make_area_file,
    lambda _: get_area_definition(),
    lambda path: load_area(make_area_file(path))
])
def test_Area(area_factory, temp_dir):
    area = Area(area=make_area_file(temp_dir)).area
    area_expected = load_area(make_area_file(temp_dir))

    assert area == area_expected
    assert isinstance(area, AreaDefinition)


@pytest.mark.parametrize(("area_factory", "msg", "exception"), [
    (
            lambda path: make_yaml_file(path / Path("chimp_nordic_4.yml"), dict(name=dict())),
            "projection",
            KeyError
    ),
    (
            lambda path: path / Path("chimp_nordic_4_non_existent.yml"),
            "point to a file",
            ValidationError
    ),
    (
            lambda _: {},
            "one item",
            ValidationError
    )
])
def test_Area_raise(area_factory, msg, exception, temp_dir):
    with pytest.raises(exception, match=msg):
        Area(area=area_factory(temp_dir))


# ======================================================
### Tests for Vertex()

@pytest.mark.parametrize("vertex", [
    Vertex(10.0, "12.3"),
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
    [10, "A"],
    [10, 20, 30]
])
@pytest.mark.parametrize("kwargs", [
    {},
    {"longitude": 10.0},
    {"longitude": 10.0, "latitude": "A"},
    {"longitude": 10.0, "latitude": 12.3, "z": 0.0}
])
def test_Vertex_raise(args, kwargs):
    with pytest.raises(ValidationError):
        Vertex(*args, **kwargs)


# ======================================================
### Tests for BoundingBox()

@pytest.mark.parametrize("bounding_box", [
    BoundingBox(10.0, 12.3, 0.0, "15.0"),
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
    [10, 20, 30, "A"],
    [10, 20, 30, 40, 50]
])
@pytest.mark.parametrize("kwargs", [
    {},
    {"north": 10.0},
    {"north": 10.0, "south": 12.3, "west": 0.0, "east": "A"},
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
    ["A"],
    [[10, 12.3]]
])
@pytest.mark.parametrize("kwargs", [
    {},
    {"vertices": None},
    {"vertices": [Vertex(10.0, 12.3)], "z": 0.0}
])
def test_Polygon_raise(args, kwargs):
    with pytest.raises(ValidationError):
        Polygon(*args, **kwargs)
