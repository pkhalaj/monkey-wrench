from datetime import datetime
from pathlib import Path

import pytest

from monkey_wrench.date_time import FilePathParser, SeviriIDParser


@pytest.mark.parametrize(("seviri_id", "expected_datetime_obj"), [
    ("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA", datetime(2015, 7, 31, 22, 12)),
    ("MSG3-SEVI-MSG15-0100-NA-20241120172743.016000000Z-NA", datetime(2024, 11, 20, 17, 27))
])
def test_seviri_id_parser(seviri_id, expected_datetime_obj):
    datetime_obj = SeviriIDParser.parse(seviri_id)
    assert expected_datetime_obj == datetime_obj


@pytest.mark.parametrize("seviri_id", [
    "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z",
    "SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
    "MSG3-NNNN-MSG15-0100-NA-20150731221240.036000000Z-NA",
    "MSG3-SEVI-MSG15-0100-NA-A0150731221240.036000000Z-NA",
    "MSG3-SEVI-MSG15-0100-NA-20150731221240-036000000Z-NA",
    "201507312212",
])
def test_seviri_id_parser_raise(seviri_id):
    with pytest.raises(ValueError, match=f"{seviri_id} into a valid datetime object"):
        SeviriIDParser.parse(seviri_id)


@pytest.mark.parametrize("filename", [
    "/home/user/dir/some_prefix_20150731_22_12.extension",
    "prefix_20150731_22_12.extension",
    "prefix_20150731_22_12",
])
def test_filename_parser(filename):
    for func in [Path, lambda x: x]:
        datetime_obj = FilePathParser.parse(func(filename))
        assert datetime_obj == datetime(2015, 7, 31, 22, 12)


@pytest.mark.parametrize("filename", [
    "/home/user/dir/some_prefix_0150731_22_12.extension",
    "some_prefix_0150731_22_12.extension",
    "0150731_22_12.extension",
    "_0150731_22_12.extension",
    "_20150731_22_12.",
    "20150731_22",
    "20150731_22_",
    "20150731_22_1",
])
def test_filename_parser_raise(filename):
    for func in [Path, lambda x: x]:
        with pytest.raises(ValueError, match="into a valid datetime object"):
            FilePathParser.parse(func(filename))
