import os
from pathlib import Path

import pytest

from monkey_wrench.input_output import write_items_to_txt_file
from monkey_wrench.input_output.seviri import input_filename_from_product_id
from monkey_wrench.task import InputFile, read_tasks_from_file
from tests.task.const import END_DATETIME, START_DATETIME, ids, ids_in_query
from tests.utils import make_dummy_files, make_yaml_file


def _verify_files_success(temp_dir):
    task_filename = Path(temp_dir, "task.yaml")
    product_ids_filename = Path(temp_dir, "product_ids.txt")
    directory = Path(temp_dir, "here")
    os.makedirs(directory, exist_ok=True)

    nominal_size = 10000
    tolerance = 0.01
    fluctuation = 0.1

    files, removed, corrupted = make_dummy_files(
        directory,
        filenames=input_filename_from_product_id(ids_in_query),
        nominal_size_in_bytes=nominal_size,
        tolerance=tolerance,
        size_fluctuation_ratio=fluctuation,
        number_of_files_to_remove=3
    )

    write_items_to_txt_file(ids, product_ids_filename)
    make_yaml_file(
        task_filename,
        dict(
            context="files",
            action="verify",
            specifications=dict(
                start_datetime=START_DATETIME,
                end_datetime=END_DATETIME,
                input_filename=str(product_ids_filename),
                input_directory=str(directory),
                nominal_size=nominal_size,
                tolerance=tolerance,
            ))
    )

    validated_task = list(read_tasks_from_file(InputFile(input_filename=task_filename)))[0]
    outs = validated_task.perform()

    keys_map = {
        "corrupted": len(corrupted),
        "missing": len(removed),
        "found": len(ids_in_query) - len(removed),
        "reference": len(ids_in_query)
    }

    for k in outs.keys():
        for p in keys_map.keys():
            if p in k:
                assert keys_map[p] == outs[k]


@pytest.mark.skip
def _fetch_files_success(get_token_or_skip, temp_dir):
    task_filename = Path(temp_dir, "task.yaml")
    product_ids_filename = Path(temp_dir, "product_ids.txt")
    write_items_to_txt_file(ids, product_ids_filename)
    directory = Path(".")
    make_yaml_file(
        task_filename,
        dict(
            context="files",
            action="fetch",
            specifications=dict(
                start_datetime=START_DATETIME,
                end_datetime=END_DATETIME,
                input_filename=str(product_ids_filename),
                output_directory=str(directory),
                number_of_processes=2,
            ))
    )

    for task in read_tasks_from_file(InputFile(input_filename=task_filename)):
        task.perform()
