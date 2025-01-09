import os
import tempfile
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from monkey_wrench import input_output
from monkey_wrench.date_time import datetime_range
from monkey_wrench.generic import Order
from monkey_wrench.query import EumetsatAPI
from tests.utils import make_dummy_file, make_dummy_files

START_DATETIME = datetime(2015, 6, 1)
END_DATETIME = datetime(2015, 6, 1, 5)
BATCH_INTERVAL = timedelta(hours=1)


@pytest.mark.parametrize("order", [
    Order.descending,
    Order.ascending
])
@pytest.mark.parametrize("pattern", [
    ".nc", ".", "nc", [".", "nc"], None, "", "2022", "non_existent_pattern"
])
def test_collect_files_in_dir(temp_dir, order, pattern):
    start_datetime = datetime(2022, 1, 1, 0, 12)
    end_datetime = datetime(2022, 1, 4)
    datetime_objs = list(datetime_range(start_datetime, end_datetime, timedelta(minutes=15)))
    if order == Order.descending:
        datetime_objs = datetime_objs[::-1]

    make_dummy_datetime_files(datetime_objs, temp_dir)
    files = input_output.visit_files_in_directory(temp_dir, order=order, pattern=pattern)

    if pattern == "non_existent_pattern":
        assert len(files) == 0
    else:
        assert len(datetime_objs) == len(files)
        for file, dt in zip(files, datetime_objs, strict=True):
            assert f"{file.stem}.nc" == str(input_output.seviri.input_filename_from_datetime(dt))

        for i in range(1, 4):
            assert os.path.exists(temp_dir / Path(f"2022/01/0{i}"))


@pytest.mark.parametrize("pattern", [
    ""
    "test_"
])
def test_copy_files_between_directories(temp_dir, pattern):
    make_dummy_files(temp_dir, prefix=pattern)
    dest_directory = Path(temp_dir, "dest_directory")
    os.makedirs(dest_directory, exist_ok=True)
    input_output.copy_files_between_directories(temp_dir, dest_directory, pattern=pattern)
    make_dummy_file(dest_directory / "excluded.ex")
    assert 4 == len(input_output.visit_files_in_directory(dest_directory))
    assert 3 == len(input_output.visit_files_in_directory(dest_directory, pattern=pattern))


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


@pytest.mark.parametrize(("func", "kwargs", "writer", "transform"), [
    (
            "query_in_batches",
            OrderedDict(start_datetime=START_DATETIME, end_datetime=END_DATETIME, batch_interval=BATCH_INTERVAL),
            input_output.write_items_to_txt_file_in_batches,
            lambda x: x
    ),
    (
            "query",
            OrderedDict(start_datetime=START_DATETIME, end_datetime=END_DATETIME),
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


def make_dummy_datetime_files(datetime_objs: list[datetime], parent: Path):
    for datetime_obj in datetime_objs:
        dir_path = input_output.create_datetime_directory(datetime_obj, parent=parent)
        filename = input_output.seviri.input_filename_from_datetime(datetime_obj)
        make_dummy_file(dir_path / filename)


def test_temp_directory():
    default_temp_path = tempfile.gettempdir()
    here_path = os.path.abspath(".")
    with input_output.temp_directory(".") as tmp:
        assert str(tmp).startswith(here_path)
        with tempfile.TemporaryDirectory() as tmpdir:
            assert tmpdir.startswith(here_path)
    assert default_temp_path == tempfile.gettempdir()
