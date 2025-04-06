import os
from pathlib import Path

import pytest

from monkey_wrench.date_time import ChimpFilePathParser, SeviriIDParser
from monkey_wrench.generic import apply_to_single_or_collection
from monkey_wrench.input_output import DirectoryVisitor, Writer
from monkey_wrench.input_output.seviri import input_filename_from_product_id
from monkey_wrench.task.common import read_tasks_from_file
from tests.geometry.test_models import get_area_definition
from tests.task.const import end_datetime, ids_in_query, start_datetime
from tests.utils import make_dummy_files, make_yaml_file


@pytest.mark.parametrize("verbose", [
    [],
    False,
    True,
    ["files"],
    ["files", "reference"],
    ["files", "missing"],
    ["files", "corrupted"],
    ["files", "reference", "missing"],
    ["files", "reference", "corrupted"],
    ["files", "missing", "corrupted"],
    ["files", "reference", "missing", "corrupted"],
    ["missing"],
    ["missing", "corrupted"],
    ["reference"],
    ["reference", "missing"],
    ["reference", "corrupted"],
    ["corrupted"]
])
def test_verify_files_success(temp_dir, verbose):
    task_filename = Path(temp_dir, "task.yaml")
    product_ids_filename = Path(temp_dir, "product_ids.txt")
    data_directory = Path(temp_dir, "data")
    os.makedirs(data_directory, exist_ok=True)

    nominal_size = 10000
    tolerance = 0.01
    fluctuation = 0.1

    files, removed, corrupted = make_dummy_files(
        data_directory,
        filenames=input_filename_from_product_id(ids_in_query),
        nominal_size_in_bytes=nominal_size,
        tolerance=tolerance,
        size_fluctuation_ratio=fluctuation,
        number_of_files_to_remove=3
    )

    Writer(output_filepath=product_ids_filename).write(ids_in_query)

    make_yaml_file(
        task_filename,
        dict(
            context="files",
            action="verify",
            specifications=dict(
                start_datetime=start_datetime.isoformat(),
                end_datetime=end_datetime.isoformat(),
                reference=dict(
                    input_filepath=str(product_ids_filename),
                    post_reading_transformation=dict(
                        transform_function="date_time.SeviriIDParser.parse"
                    )
                ),
                filepaths=dict(parent_input_directory_path=str(data_directory)),
                nominal_file_size=nominal_size,
                filepath_transform_function="date_time.ChimpFilePathParser.parse",
                file_size_relative_tolerance=tolerance,
                verbose=verbose,
            ))
    )

    if verbose is True:
        verbose = ["files", "reference", "missing", "corrupted"]
    if verbose is False:
        verbose = []

    validated_task = list(read_tasks_from_file(task_filename))[0]
    outs = validated_task.perform()

    missing = apply_to_single_or_collection(ChimpFilePathParser.parse, removed)
    reference = apply_to_single_or_collection(SeviriIDParser.parse, ids_in_query)
    files = apply_to_single_or_collection(input_filename_from_product_id, ids_in_query)
    files = {data_directory / f for f in files} - set(removed)
    files = sorted(list(files))

    keys_map = {
        "corrupted files": verbose_or_not(corrupted, "corrupted", verbose),
        "missing items": verbose_or_not(missing, "missing", verbose),
        "files found": verbose_or_not(files, "files", verbose),
        "reference items": verbose_or_not(reference, "reference", verbose),
    }

    for k in outs.keys():
        for p in keys_map.keys():
            if p in k:
                assert outs[k] == keys_map[p]


def verbose_or_not(field, field_name, verbose):
    if field_name in verbose:
        return field
    return len(field)


def test_fetch_files(get_token_or_skip, temp_dir):
    task_filename = Path(temp_dir, "task.yaml")
    product_ids_filename = Path(temp_dir, "product_ids.txt")
    parent_directory = temp_dir / Path("output")
    os.makedirs(parent_directory, exist_ok=True)
    Writer(output_filepath=product_ids_filename).write(ids_in_query[:2])

    make_yaml_file(
        task_filename,
        dict(
            context="files",
            action="fetch",
            specifications=dict(
                area=get_area_definition(),
                fsspec_cache="filecache",
                start_datetime=start_datetime.isoformat(),
                end_datetime=end_datetime.isoformat(),
                input_filepath=str(product_ids_filename),
                parent_output_directory_path=str(parent_directory),
                number_of_processes=2,
                temp_directory_path=str(temp_dir),
            )
        )
    )

    for task in read_tasks_from_file(task_filename):
        task.perform()

    paths = DirectoryVisitor(parent_input_directory_path=parent_directory).visit()
    assert {str(p.stem) for p in paths} == {"seviri_20230101_01_57", "seviri_20230101_02_12"}
