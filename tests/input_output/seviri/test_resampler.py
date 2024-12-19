from pathlib import Path

import pytest
from pyresample import load_area
from satpy.readers import FSFile

from monkey_wrench.input_output.seviri import resample_seviri_native_file
from tests.utils import make_dummy_file, make_yaml_file

AREA_DEFINITION = dict(
    CHIMP_NORDIC=dict(
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


def get_area_from_chimp(temp_dir):
    return load_area(make_yaml_file(temp_dir / Path("chimp_nordic_4.yml"), AREA_DEFINITION))


@pytest.mark.parametrize(("filename", "error_message", "area_func"), [
    ("test", "does not end with `.nc`", get_area_from_chimp),
    ("test.nc", "Invalid area", lambda _: AREA_DEFINITION)
])
def test_resample_seviri_native_file_raise(temp_dir, filename, error_message, area_func):
    area = area_func(temp_dir)
    with pytest.raises(ValueError, match=error_message):
        resample_seviri_native_file(make_fs_file(temp_dir, filename), temp_dir, lambda x: x, area)


@pytest.mark.parametrize("area_func", [
    lambda x: make_yaml_file(x / Path("sample_area.yaml"), AREA_DEFINITION),
    get_area_from_chimp,
])
def test_resample_seviri_native_file_with_area(temp_dir, area_func):
    fs_file = make_fs_file(temp_dir, "test.nc")
    area = area_func(temp_dir)
    with pytest.raises(ValueError, match="No supported files"):
        resample_seviri_native_file(fs_file, temp_dir, lambda x: x, area=area)


def make_fs_file(directory: Path, filename: str) -> FSFile:
    return FSFile(make_dummy_file(directory / Path(filename)))
