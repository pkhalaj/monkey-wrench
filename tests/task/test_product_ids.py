from datetime import datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from monkey_wrench.date_time import SeviriIDParser
from monkey_wrench.input_output import Reader
from monkey_wrench.task.common import read_tasks_from_file
from monkey_wrench.task.ids import Fetch
from tests.task.const import (
    batch_interval,
    end_datetime,
    future_datetime,
    output_filepath,
    specification_with,
    start_datetime,
    task,
    task_with,
)
from tests.utils import make_yaml_file


@pytest.mark.parametrize("task_factory", [
    lambda path: get_validated_task(path),
    lambda path: get_validated_task(path, start_datetime=start_datetime.isoformat()),
    lambda _: Fetch(**specification_with(batch_interval=timedelta(**batch_interval)))
])
def test_model_product_ids(temp_dir, task_factory):
    validated_task = task_factory(temp_dir)

    assert task["context"] == validated_task.context
    assert task["action"] == validated_task.action
    assert start_datetime == validated_task.specifications.start_datetime
    assert end_datetime == validated_task.specifications.end_datetime
    assert timedelta(**batch_interval) == validated_task.specifications.batch_interval
    assert Path(output_filepath).absolute() == validated_task.specifications.output_filepath


def get_validated_task(path: Path, **kwargs):
    filename = Path(path, "task.yaml")
    make_yaml_file(filename, specification_with(**kwargs))
    validated_task = list(read_tasks_from_file(filename))[0]
    return validated_task


@pytest.mark.parametrize(("task", "error_message"), [
    (specification_with(start_datetime=["A"]), "datetime"),
    (specification_with(end_datetime=[1]), "datetime"),
    (specification_with(end_datetime=datetime(2000, 1, 1)), "timezone"),
    (specification_with(start_datetime=future_datetime), "future"),
    (task | dict(extra_argument="extra arguments are not allowed!"), "Extra inputs"),
    (task_with(context="non_existent_context"), "Input should be"),
    (task_with(action="non_existent_action"), "Input should be"),
])
def test_model_product_ids_raise(temp_dir, task, error_message):
    filename = Path(temp_dir, "task.yaml")
    make_yaml_file(filename, task)
    with pytest.raises(ValidationError, match=error_message):
        list(read_tasks_from_file(filename))


def test_fetch_product_ids_success(get_token_or_skip, temp_dir):
    filename = Path(temp_dir, "task.yaml")
    output_filename = Path(temp_dir, "products_ids.txt")
    make_yaml_file(filename, specification_with(output_filepath=str(output_filename)))

    validated_task = list(read_tasks_from_file(filename))[0]
    validated_task.perform()

    data = Reader(input_filepath=validated_task.specifications.output_filepath).read()
    for product in data:
        assert start_datetime <= SeviriIDParser.parse(product) < end_datetime
