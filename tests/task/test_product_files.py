import os
from pathlib import Path

from monkey_wrench.input_output import ExistingInputFile, Writer
from monkey_wrench.input_output.seviri import input_filename_from_product_id
from monkey_wrench.task.common import read_tasks_from_file
from tests.geometry.test_models import get_area_definition
from tests.task.const import end_datetime, ids_in_query, start_datetime
from tests.utils import make_dummy_files, make_yaml_file


def test_verify_files_success(temp_dir):
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
                reference=str(product_ids_filename),
                parent_directory=str(data_directory),
                nominal_file_size=nominal_size,
                file_size_relative_tolerance=tolerance,
            ))
    )

    validated_task = list(read_tasks_from_file(ExistingInputFile(input_filepath=task_filename)))[0]
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
                assert outs[k] == keys_map[p]


def test_fetch_files(get_token_or_skip, temp_dir):
    task_filename = Path(temp_dir, "task.yaml")
    product_ids_filename = Path(temp_dir, "product_ids.txt")
    Writer(output_filepath=product_ids_filename).write(ids_in_query[:2])

    make_yaml_file(
        task_filename,
        dict(
            context="files",
            action="fetch",
            specifications=dict(
                area=get_area_definition(),
                cache="filecache",
                start_datetime=start_datetime.isoformat(),
                end_datetime=end_datetime.isoformat(),
                input_filepath=str(product_ids_filename),
                parent_directory=str(temp_dir),
                number_of_processes=2,
                temp_directory=str(temp_dir),
            )
        )
    )

    for task in read_tasks_from_file(ExistingInputFile(input_filepath=task_filename)):
        task.perform()
