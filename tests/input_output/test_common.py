import os
import tempfile
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from monkey_wrench import input_output
from monkey_wrench.date_time import datetime_range
from monkey_wrench.query import EumetsatAPI
from tests.utils import make_dummy_datetime_files, make_dummy_file, make_dummy_files

start_datetime = datetime(2022, 1, 1, 0, 12)
end_datetime = datetime(2022, 1, 4)
batch_interval = timedelta(hours=1)
number_of_days = (end_datetime - start_datetime).days


# ======================================================
### Tests for visit_files_in_directory()

@pytest.mark.parametrize("reverse", [
    True,
    False
])
@pytest.mark.parametrize("pattern", [
    ".nc", ".", "nc", [".", "nc"], None, "", "2022", "non_existent_pattern"
])
def test_visit_files_in_directory(temp_dir, reverse, pattern):
    datetime_objects = _make_dummy_files(temp_dir, reverse)
    files = input_output.visit_files_in_directory(temp_dir, reverse=reverse, pattern=pattern)

    if pattern == "non_existent_pattern":
        assert len(files) == 0
    else:
        assert len(datetime_objects) == len(files)
        _assert_filenames_match_filenames_from_datetime(datetime_objects, files)
        _assert_datetime_directories_exist(temp_dir)


def _assert_datetime_directories_exist(temp_dir):
    for i in range(1, number_of_days + 1):
        assert os.path.exists(temp_dir / Path(f"2022/01/0{i}"))


def _assert_filenames_match_filenames_from_datetime(datetime_objects, files):
    for file, datetime_ in zip(files, datetime_objects, strict=True):
        assert f"{file.stem}.nc" == str(input_output.seviri.input_filename_from_datetime(datetime_))


def _make_dummy_files(temp_dir, reverse):
    datetime_objs = list(datetime_range(start_datetime, end_datetime, batch_interval))
    if reverse:
        datetime_objs = datetime_objs[::-1]
    make_dummy_datetime_files(datetime_objs, temp_dir)
    return datetime_objs


# ======================================================
### Tests for copy_files_between_directories()

@pytest.mark.parametrize("pattern", [
    ""
    "file_for_test_"
])
def test_copy_files_between_directories(temp_dir, pattern):
    make_dummy_files(temp_dir, prefix=pattern)
    dest_directory = Path(temp_dir, "dest_directory")
    os.makedirs(dest_directory, exist_ok=True)
    input_output.copy_files_between_directories(temp_dir, dest_directory, pattern=pattern)
    make_dummy_file(dest_directory / "excluded.ex")

    assert 4 == len(input_output.visit_files_in_directory(dest_directory))
    assert 3 == len(input_output.visit_files_in_directory(dest_directory, pattern=pattern))


# ======================================================
### Tests for compare_files_against_reference()

def test_compare_files_against_reference(temp_dir):
    nominal_size = 10000
    tolerance = 0.05
    files, expected_missing, expected_corrupted = make_dummy_files(temp_dir, number_of_files_to_remove=3)

    collected_files = input_output.visit_files_in_directory(temp_dir)
    missing_files, corrupted_files = input_output.compare_files_against_reference(
        collected_files, reference_items=files, nominal_size=nominal_size, tolerance=tolerance, number_of_processes=1
    )
    assert (expected_missing, expected_corrupted) == (missing_files, corrupted_files)

    missing_files, corrupted_files = input_output.compare_files_against_reference(
        collected_files, number_of_processes=1
    )
    assert (None, None) == (missing_files, corrupted_files)

    missing_files, corrupted_files = input_output.compare_files_against_reference(
        collected_files, files, number_of_processes=1
    )
    assert (expected_missing, None) == (missing_files, corrupted_files)

    missing_files, corrupted_files = input_output.compare_files_against_reference(
        collected_files, nominal_size=nominal_size, tolerance=tolerance, number_of_processes=1
    )
    assert (None, expected_corrupted) == (missing_files, corrupted_files)


# ======================================================
### Tests for compare_files_against_reference()

@pytest.mark.parametrize(("func", "kwargs", "writer", "transform"), [
    (
            "query_in_batches",
            OrderedDict(start_datetime=start_datetime, end_datetime=end_datetime, batch_interval=batch_interval),
            input_output.write_items_to_txt_file_in_batches,
            lambda x: x
    ),
    (
            "query",
            OrderedDict(start_datetime=start_datetime, end_datetime=end_datetime),
            input_output.write_items_to_txt_file,
            lambda x: list(x)),
])
def test_write_to_file_and_read_from_file(temp_dir, get_token_or_skip, func, kwargs, writer, transform):
    product_ids = [
        "20150601045740.599", "20150601044240.763", "20150601042740.925", "20150601041241.084",
        "20150601035741.242", "20150601034241.398", "20150601032741.551", "20150601031239.899",
        "20150601025740.047", "20150601024240.194", "20150601022740.339", "20150601021240.481",
        "20150601015740.621", "20150601014240.760", "20150601012740.897", "20150601011241.032",
        "20150601005739.963", "20150601004240.094", "20150601002740.223", "20150601001240.351"
    ]
    expected_product_ids = {f"MSG3-SEVI-MSG15-0100-NA-{p}000000Z-NA" for p in product_ids}
    api_query = EumetsatAPI()
    products = transform(getattr(api_query, func)(**kwargs))
    writer(products, temp_dir / Path("seviri_product_ids.txt"))

    product_ids = set(input_output.read_items_from_txt_file(temp_dir / Path("seviri_product_ids.txt")))
    assert expected_product_ids == product_ids


def test_create_datetime_dir(temp_dir):
    dir_path = input_output.create_datetime_directory(datetime(2022, 3, 12), parent=temp_dir)
    assert temp_dir / Path("2022/03/12") == dir_path


def test_temp_directory():
    default_temp_path = tempfile.gettempdir()
    here_path = os.path.abspath(".")
    with input_output.temp_directory(".") as tmp:
        assert str(tmp).startswith(here_path)
        with tempfile.TemporaryDirectory() as tmpdir:
            assert tmpdir.startswith(here_path)
    assert default_temp_path == tempfile.gettempdir()
