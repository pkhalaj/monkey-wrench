from datetime import UTC, datetime
from pathlib import Path

import pytest

from monkey_wrench.date_time import (
    ChimpFilePathParser,
    DateTimeParserBase,
    FCIIDParser,
    HritFilePathParser,
    SeviriIDParser,
)

# ======================================================
### Tests for DateTimeParserBase()

@pytest.mark.parametrize("inp", [
    datetime(2000, 1, 1, tzinfo=UTC),
    None,
    "2022",
    2022
])
def test_DateTimeParserBase_parse(inp):
    assert DateTimeParserBase.parse(inp) == inp


@pytest.mark.parametrize(("datetime_string", "datetime_tuple"), [
    ("20230102_22_30", (2023, 1, 2, 22, 30)),
    ("20001212_21_41", (2000, 12, 12, 21, 41))
])
def test_DateTimeParserBase_parse_by_regex(datetime_string, datetime_tuple):
    regex = r"^(19|20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_(0\d|1\d|2[0-3])_([0-5]\d)$"
    parsed = DateTimeParserBase.parse_by_regex(datetime_string, regex)
    assert datetime(*datetime_tuple, tzinfo=UTC) == parsed


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
def test_DateTimeParserBase_parse_by_regex_raise(datetime_string):
    regex = r"^(19|20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_(0\d|1\d|2[0-3])_([0-5]\d)$"
    with pytest.raises(ValueError, match="parse"):
        DateTimeParserBase.parse_by_regex(datetime_string, regex)


@pytest.mark.parametrize(("datetime_string", "datetime_tuple"), [
    ("20230102_22_30", (2023, 1, 2, 22, 30)),
    ("20001212_21_41", (2000, 12, 12, 21, 41)),
    ("19980101_12_3", (1998, 1, 1, 12, 3))
])
def test_DateTimeParserBase_parse_by_format(datetime_string, datetime_tuple):
    parsed = DateTimeParserBase.parse_by_format_string(datetime_string, "%Y%m%d_%H_%M")
    assert datetime(*datetime_tuple, tzinfo=UTC) == parsed


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
def test_DateTimeParserBase_parse_by_format_raise(datetime_string):
    with pytest.raises(ValueError, match="parse"):
        DateTimeParserBase.parse_by_format_string(datetime_string, "%Y%m%d_%H_%M")


# ======================================================
### Tests for SeviriIDParser()

@pytest.mark.parametrize(("seviri_id", "expected_datetime_tuple"), [
    ("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA", (2015, 7, 31, 22, 12)),
    ("MSG3-SEVI-MSG15-0100-NA-20241120172743.016000000Z-NA", (2024, 11, 20, 17, 27)),
    ("MSG3-SEVI-MSG15-0100-NA-20250102001243.365000000Z-NA", (2025, 1, 2, 0, 12))
])
def test_SeviriIDParser_parse(seviri_id, expected_datetime_tuple):
    datetime_obj = SeviriIDParser.parse(seviri_id)
    assert datetime(*expected_datetime_tuple, tzinfo=UTC) == datetime_obj


def test_SeviriIDParser_parse_collection():
    seviri_ids = [
        "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
        "MSG3-SEVI-MSG15-0100-NA-20241120172743.016000000Z-NA"
    ]
    datetime_objects = [
        datetime(2015, 7, 31, 22, 12, tzinfo=UTC),
        datetime(2024, 11, 20, 17, 27, tzinfo=UTC),
    ]
    assert datetime_objects == SeviriIDParser.parse_collection(seviri_ids)


@pytest.mark.parametrize("seviri_id", [
    "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z",
    "SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
    "MSG3-NNNN-MSG15-0100-NA-20150731221240.036000000Z-NA",
    "MSG3-SEVI-MSG15-0100-NA-A0150731221240.036000000Z-NA",
    "MSG3-SEVI-MSG15-0100-NA-20150731221240-036000000Z-NA",
    "201507312212",
])
def test_SeviriIDParser_parse_raise(seviri_id):
    with pytest.raises(ValueError, match=f"{seviri_id} into a valid datetime object"):
        SeviriIDParser.parse(seviri_id)


# ======================================================
### Tests for FCIIDParser()

@pytest.mark.parametrize(("fci_id", "expected_datetime_tuple"), [
    (
            "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-FDHSI-FD--x-x---x_C_EUMT_20251216091032_IDPFI_OPE_20251216091007_20251216091923_N__O_0056_0000",
            (2025, 12, 16, 9, 10)
    ),
    (
            "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-HRFI-FD--x-x---x_C_EUMT_20251230220247_IDPFI_OPE_20251230220007_20251230220928_N__O_0133_0000",
            (2025, 12, 30, 22, 0)
    ),
    (
            "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-FDHSI-FD--x-x---x_C_EUMT_20250102000318_IDPFI_OPE_20250102000007_20250102000928_N__O_0001_0000",
            (2025, 1, 2, 0, 0)
    )
])
def test_FCIIDParser_parse(fci_id, expected_datetime_tuple):
    datetime_obj = FCIIDParser.parse(fci_id)
    assert datetime(*expected_datetime_tuple, tzinfo=UTC) == datetime_obj


def test_FCIIDParser_parse_collection():
    fci_ids = [
        "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-FDHSI-FD--x-x---x_C_EUMT_20251216091032_IDPFI_OPE_20251216091007_20251216091923_N__O_0056_0000",
        "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-HRFI-FD--x-x---x_C_EUMT_20251230220247_IDPFI_OPE_20251230220007_20251230220928_N__O_0133_0000"
    ]
    datetime_objects = [
        datetime(2025, 12, 16, 9, 10, tzinfo=UTC),
        datetime(2025, 12, 30, 22, 0, tzinfo=UTC),
    ]
    assert datetime_objects == FCIIDParser.parse_collection(fci_ids)


@pytest.mark.parametrize("fci_id", [
    "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-FDHSI-FD--x-x---x_C_EUMT",
    "_EUMT_20251216091032_IDPFI_OPE_20250016091007_20251216091923_N__O_0056_0000",
])
def test_FCIIDParser_parse_raise(fci_id):
    with pytest.raises(ValueError, match="into a valid datetime object"):
        FCIIDParser.parse(fci_id)


# ======================================================
### Tests for ChimpFilePathParser()

@pytest.mark.parametrize("filename", [
    "/home/user/dir/some_prefix_20150731_22_12.extension",
    "prefix_20150731_22_12.extension",
    "prefix_20150731_22_12",
    "prefix_20150731_22_1272",
    "some_prefix_20150731_22_12"
])
def test_FilePathParser_parse(filename):
    for func in [Path, lambda x: x]:
        datetime_obj = ChimpFilePathParser.parse(func(filename))
        assert datetime(2015, 7, 31, 22, 12, tzinfo=UTC) == datetime_obj


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
def test_FilePathParser_parse_raise(filename):
    for func in [Path, lambda x: x]:
        with pytest.raises(ValueError, match="into a valid datetime object"):
            ChimpFilePathParser.parse(func(filename))


# ======================================================
### Tests for HritFilePathParser()

@pytest.mark.parametrize("path", [
    "/home/user/dir",
    ""
])
@pytest.mark.parametrize("filename", [
    "H-000-MSG3__-MSG3________-WV_073___-000007___-201507312212-__",
    "201507312212-__",
    "prefx201507312212-__",
])
def test_HritFilePathParser_parse(path, filename):
    for func in [Path, lambda x: x]:
        datetime_obj = HritFilePathParser.parse(func(path + filename))
        assert datetime(2015, 7, 31, 22, 12, tzinfo=UTC) == datetime_obj

    with pytest.raises(ValueError, match="into a valid datetime object"):
        ChimpFilePathParser.parse(func(path + filename + "-"))
