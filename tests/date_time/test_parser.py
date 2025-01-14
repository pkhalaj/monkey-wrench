from datetime import datetime
from pathlib import Path

import pytest

from monkey_wrench.date_time import DateTimeParserBase, FilePathParser, SeviriIDParser

# ======================================================
### Tests for DateTimeParserBase

def _DateTimeParserBase_parse_raise():
    with pytest.raises(NotImplementedError):
        DateTimeParserBase.parse(None)


@pytest.mark.parametrize(("datetime_string", "datetime_tuple"), [
    ("20230102_22_30", (2023, 1, 2, 22, 30)),
    ("20001212_21_41", (2000, 12, 12, 21, 41))
])
def _DateTimeParserBase_parse_by_regex(datetime_string, datetime_tuple):
    regex = r"^(19|20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_(0\d|1\d|2[0-3])_([0-5]\d)$"
    parsed = DateTimeParserBase.parse_by_regex(datetime_string, regex)
    assert datetime(*datetime_tuple) == parsed


@pytest.mark.parametrize("datetime_string", [
    "202301022230",
    "YYYYmmDD_HH_MM",
    "00230102_22_30",
    "230102_22_30_23",
    "2301022_22_61",
    "2301322_22_30",
    "2301232_22_30",
    "2301022_22_30",
    "202301022_22_3",
    "2301022_22_30_",
    "_2301022_22_30"
])
def _DateTimeParserBase_parse_by_regex_raise(datetime_string):
    regex = r"^(19|20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_(0\d|1\d|2[0-3])_([0-5]\d)$"
    with pytest.raises(ValueError, match="parse"):
        DateTimeParserBase.parse_by_regex(datetime_string, regex)


@pytest.mark.parametrize(("datetime_string", "datetime_tuple"), [
    ("20230102_22_30", (2023, 1, 2, 22, 30)),
    ("20001212_21_41", (2000, 12, 12, 21, 41)),
    ("19980101_12_3", (1998, 1, 1, 12, 3))
])
def _DateTimeParserBase_parse_by_format(datetime_string, datetime_tuple):
    parsed = DateTimeParserBase.parse_by_format_string(datetime_string, "%Y%m%d_%H_%M")
    assert datetime(*datetime_tuple) == parsed


@pytest.mark.parametrize("datetime_string", [
    "202301022230",
    "YYYYmmDD_HH_MM",
    "230102_22_30_23",
    "20230102_22_61",
    "20231232_22_30",
    "20231422_22_30",
    "20230102_22_30_",
    "_20230102_22_30"
])
def _DateTimeParserBase_parse_by_format_raise(datetime_string):
    with pytest.raises(ValueError, match="parse"):
        DateTimeParserBase.parse_by_format_string(datetime_string, "%Y%m%d_%H_%M")


# ======================================================
### Tests for SeviriIDParser

@pytest.mark.parametrize(("seviri_id", "expected_datetime_tuple"), [
    ("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA", (2015, 7, 31, 22, 12)),
    ("MSG3-SEVI-MSG15-0100-NA-20241120172743.016000000Z-NA", (2024, 11, 20, 17, 27))
])
def _SeviriIDParser_parse(seviri_id, expected_datetime_tuple):
    datetime_obj = SeviriIDParser.parse(seviri_id)
    assert datetime(*expected_datetime_tuple) == datetime_obj


@pytest.mark.parametrize("seviri_id", [
    "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z",
    "SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
    "MSG3-NNNN-MSG15-0100-NA-20150731221240.036000000Z-NA",
    "MSG3-SEVI-MSG15-0100-NA-A0150731221240.036000000Z-NA",
    "MSG3-SEVI-MSG15-0100-NA-20150731221240-036000000Z-NA",
    "201507312212",
])
def _SeviriIDParser_parse_raise(seviri_id):
    with pytest.raises(ValueError, match=f"{seviri_id} into a valid datetime object"):
        SeviriIDParser.parse(seviri_id)


# ======================================================
### Tests for FilePathParser

@pytest.mark.parametrize("filename", [
    "/home/user/dir/some_prefix_20150731_22_12.extension",
    "prefix_20150731_22_12.extension",
    "prefix_20150731_22_12",
    "prefix_20150731_22_1272",
    "some_prefix_20150731_22_12"
])
def _FilePathParser_parse(filename):
    for func in [Path, lambda x: x]:
        datetime_obj = FilePathParser.parse(func(filename))
        assert datetime_obj == datetime(2015, 7, 31, 22, 12)


@pytest.mark.parametrize("filename", [
    "/home/user/dir/some_prefix_0150731_22_12.extension",
    "some_prefix_0150731_22_12.extension",
    "0150731_22_12.extension",
    "_0150731_22_12.extension",
    "_20150731_22_12.",
    "_20150731_22_12"
    "20150731_22",
    "20150731_22_",
    "20150731_22_1",
])
def _FilePathParser_parse_raise(filename):
    for func in [Path, lambda x: x]:
        with pytest.raises(ValueError, match="into a valid datetime object"):
            FilePathParser.parse(func(filename))
