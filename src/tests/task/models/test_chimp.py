import os
from contextlib import contextmanager
from pathlib import Path

from chimp import processing

from monkey_wrench.input_output.seviri import input_filename_from_product_id
from monkey_wrench.task import read_tasks_from_file
from monkey_wrench.test_utils import make_dummy_file, make_dummy_files, make_yaml_file

from ..const import END_DATETIME, START_DATETIME, ids


def noop(*_args, **_kwargs):
    pass


@contextmanager
def dummy_chimp_cli():
    _cli = processing.cli
    processing.cli = noop

    try:
        yield
    finally:
        processing.cli = _cli


def test_retrieve_success(temp_dir):
    task_filename = Path(temp_dir, "task.yaml")

    model_dir = Path(temp_dir, "model_dir")
    input_dir = Path(temp_dir, "input_dir")
    output_dir = Path(temp_dir, "output_dir")
    temp_dir_ = Path(temp_dir, "temp_dir")

    for d in [model_dir, input_dir, output_dir, temp_dir_]:
        os.makedirs(d, exist_ok=True)

    model_file = make_dummy_file(Path(model_dir, "chimp_smhi_v3_seq.pt"))

    files, _, _ = make_dummy_files(
        input_dir,
        filenames=input_filename_from_product_id(ids),
        nominal_size_in_bytes=12334248,
        tolerance=0.01,
        number_of_files_to_remove=0
    )

    make_yaml_file(
        task_filename,
        dict(
            context="chimp",
            action="retrieve",
            specifications=dict(
                start_datetime=START_DATETIME,
                end_datetime=END_DATETIME,
                model_filename=str(model_file),
                input_directory=str(input_dir),
                output_directory=str(output_dir),
                temp_directory=str(temp_dir_),
                device="cpu"
            ))
    )

    with dummy_chimp_cli():
        validated_task = list(read_tasks_from_file(task_filename))[0]
        validated_task.perform()
