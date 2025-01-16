import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from monkey_wrench import input_output
from monkey_wrench.date_time import FilePathParser, datetime_range
from tests.utils import make_dummy_datetime_files, make_dummy_file, make_dummy_files

start_datetime = datetime(2022, 1, 1, 0, 12)
end_datetime = datetime(2022, 1, 4)
batch_interval = timedelta(hours=1)
number_of_days = (end_datetime - start_datetime).days


# ======================================================
### Tests for visit_files_in_directory()

@pytest.mark.parametrize("reverse", [
    True, False
])
@pytest.mark.parametrize("recursive", [
    True, False
])
@pytest.mark.parametrize("pattern", [
    ".nc", ".", "nc", [".", "nc"], None, "", "2022", "non_existent_pattern"
])
def test_visit_files_in_directory(temp_dir, reverse, pattern, recursive):
    datetime_objects, _ = _make_dummy_datetime_files(temp_dir, reverse)
    top_level_files, _, _ = make_dummy_files(temp_dir, prefix="top_level_files_2022.nc")
    files = input_output.visit_files_in_directory(temp_dir, reverse=reverse, pattern=pattern, recursive=recursive)

    if pattern == "non_existent_pattern":
        assert len(files) == 0
    else:
        if recursive:
            assert len(datetime_objects) + len(top_level_files) == len(files)
            files = [f for f in files if "top_level" not in str(f)]
            _assert_filenames_match_filenames_from_datetime(files, datetime_objects)
        else:
            assert top_level_files == set(files)


def test_visit_files_in_directory_callback(temp_dir):
    buff = []
    _, dummy_files = _make_dummy_datetime_files(temp_dir)
    files = input_output.visit_files_in_directory(temp_dir, callback=lambda x: buff.append(x))

    assert set(files) == set(buff)
    assert set(dummy_files) == set(buff)


def _assert_datetime_directories_exist(temp_dir):
    for i in range(1, number_of_days + 1):
        assert os.path.exists(temp_dir / Path(f"2022/01/0{i}"))


def _assert_filenames_match_filenames_from_datetime(files, datetime_objects):
    for file, datetime_ in zip(files, datetime_objects, strict=True):
        assert f"{file.stem}.nc" == str(input_output.seviri.input_filename_from_datetime(datetime_))


def _make_dummy_datetime_files(temp_dir, reverse=False):
    datetime_objs = list(datetime_range(start_datetime, end_datetime, batch_interval))
    if reverse:
        datetime_objs = datetime_objs[::-1]
    files = make_dummy_datetime_files(datetime_objs, temp_dir)
    _assert_datetime_directories_exist(temp_dir)
    return datetime_objs, files


# ======================================================
### Tests for copy_files_between_directories()

@pytest.mark.parametrize("pattern", [
    ""
    "file_for_test_"
])
def test_copy_files_between_directories(temp_dir, pattern):
    dest_directory = _make_dummy_files_for_copy(temp_dir, pattern)
    input_output.copy_files_between_directories(temp_dir, dest_directory, pattern=pattern)

    assert 4 == len(input_output.visit_files_in_directory(dest_directory))
    assert 3 == len(input_output.visit_files_in_directory(dest_directory, pattern=pattern))


def _make_dummy_files_for_copy(temp_dir, pattern):
    make_dummy_files(temp_dir, prefix=pattern)
    dest_directory = Path(temp_dir, "dest_directory")
    os.makedirs(dest_directory, exist_ok=True)
    make_dummy_file(dest_directory / "excluded.ex")
    return dest_directory


# ======================================================
### Tests for compare_files_against_reference()

@pytest.mark.parametrize(("expected", "keys"), [
    (("expected_missing", "expected_corrupted"),
     ("reference_items", "nominal_size", "tolerance", "number_of_processes")),
    ((None, None), ("number_of_processes",)),
    (("expected_missing", None), ("reference_items", "number_of_processes")),
    ((None, "expected_corrupted"), ("nominal_size", "tolerance", "number_of_processes")),
])
def test_compare_files_against_reference(dummy_and_reference_files_for_comparison, expected, keys):
    collected_files, files_information = dummy_and_reference_files_for_comparison

    kwargs = {k: files_information[k] for k in keys}
    expected_ = tuple(files_information.get(i) for i in expected)
    assert expected_ == input_output.compare_files_against_reference(collected_files, **kwargs)


def test_compare_files_against_reference_transform(temp_dir):
    datetime_objs, collected_files = _make_dummy_datetime_files(temp_dir)

    missing, _ = input_output.compare_files_against_reference(
        collected_files, reference_items=datetime_objs, transform_function=FilePathParser.parse)

    assert missing == set()


@pytest.fixture
def dummy_and_reference_files_for_comparison(temp_dir):
    reference_items, expected_missing, expected_corrupted = make_dummy_files(temp_dir, number_of_files_to_remove=3)
    collected_files = input_output.visit_files_in_directory(temp_dir)
    items = dict(
        nominal_size=1000,
        tolerance=0.05,
        reference_items=reference_items,
        expected_missing=expected_missing,
        expected_corrupted=expected_corrupted,
        number_of_processes=1,
        none=None
    )
    return collected_files, items


# ======================================================
### Tests for
#               write_items_to_txt_file
#               write_items_to_txt_file_in_batches
#               read_items_from_txt_file

@pytest.mark.parametrize(("writer", "transform"), [
    (
            input_output.write_items_to_txt_file_in_batches,
            lambda x: (([x], 1) for x in x)
    ),
    (
            input_output.write_items_to_txt_file,
            lambda x: x
    ),
])
def test_write_to_file_and_read_from_file(seviri_product_ids_file, writer, transform):
    product_ids = [
        "20150601045740.599", "20150601044240.763", "20150601042740.925", "20150601041241.084",
        "20150601035741.242", "20150601034241.398", "20150601032741.551", "20150601031239.899",
        "20150601025740.047", "20150601024240.194", "20150601022740.339", "20150601021240.481",
        "20150601015740.621", "20150601014240.760", "20150601012740.897", "20150601011241.032",
        "20150601005739.963", "20150601004240.094", "20150601002740.223", "20150601001240.351"
    ]
    expected_product_ids = [f"MSG3-SEVI-MSG15-0100-NA-{p}000000Z-NA" for p in product_ids]
    product_ids = transform(expected_product_ids)

    writer(product_ids, seviri_product_ids_file)
    read_product_ids = input_output.read_items_from_txt_file(seviri_product_ids_file)
    assert expected_product_ids == read_product_ids


@pytest.fixture
def seviri_product_ids_file(temp_dir):
    return temp_dir / Path("seviri_product_ids.txt")


# ======================================================
### Tests for create_datetime_directory()

@pytest.mark.parametrize("kwargs", [
    dict(format_string="%Y/%m/%d", dry_run=False),
    dict(format_string="%Y/%m/%d", dry_run=True),
    dict(format_string="%Y-%m/%d", dry_run=False),
    dict(format_string="%Y-%m/%d", dry_run=True),
])
def test_create_datetime_dir(temp_dir, kwargs):
    datetime_obj = datetime(2022, 3, 12)
    dir_path = input_output.create_datetime_directory(
        datetime_obj,
        parent=temp_dir,
        **kwargs
    )
    if not kwargs["dry_run"]:
        assert dir_path.exists()
    assert temp_dir / Path(datetime_obj.strftime(kwargs["format_string"])) == dir_path


# ======================================================
### Tests for temp_directory()

def test_temp_directory():
    default_temp_path = tempfile.gettempdir()
    here_path = os.path.abspath(".")
    with input_output.temp_directory(".") as tmp:
        assert str(tmp).startswith(here_path)
        with tempfile.TemporaryDirectory() as tmpdir:
            assert tmpdir.startswith(here_path)
    assert default_temp_path == tempfile.gettempdir()
