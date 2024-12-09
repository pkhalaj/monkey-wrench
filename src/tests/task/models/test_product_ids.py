from datetime import datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from monkey_wrench.date_time import SeviriIDParser
from monkey_wrench.input_output import read_items_from_txt_file
from monkey_wrench.task import read_tasks_from_file
from monkey_wrench.test_utils import make_yaml_file

from ..const import (
    BATCH_INTERVAL,
    END_DATETIME,
    FUTURE_DATETIME,
    OUTPUT_FILENAME,
    START_DATETIME,
    specification_with,
    task,
    task_with,
)


def test_model_product_ids_success(temp_dir):
    filename = Path(temp_dir, "task.yaml")
    make_yaml_file(filename, task)
    validated_task = list(read_tasks_from_file(filename))[0]

    assert task["context"] == validated_task.context
    assert task["action"] == validated_task.action

    assert datetime(*START_DATETIME) == validated_task.specifications.start_datetime
    assert datetime(*END_DATETIME) == validated_task.specifications.end_datetime
    assert timedelta(**BATCH_INTERVAL) == validated_task.specifications.batch_interval
    assert Path(OUTPUT_FILENAME).absolute() == validated_task.specifications.output_filename


@pytest.mark.parametrize(("task", "error_message"), [
    (specification_with(start_datetime=1), "must be a list"),
    (specification_with(start_datetime=["A"]), "must be integer"),
    (specification_with(end_datetime=[-1]), "must be positive"),
    (specification_with(start_datetime=FUTURE_DATETIME), "should be in the past"),
    (specification_with(end_datetime=FUTURE_DATETIME), "should be in the past"),
    (specification_with(start_datetime=END_DATETIME, end_datetime=START_DATETIME), "is later than"),
    (specification_with(output_filename="./this_is_directory_like/"), "cannot end with a '/'"),
    (specification_with(output_filename=__file__), "already exists"),
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
    make_yaml_file(filename, specification_with(output_filename=str(output_filename)))

    validated_task = list(read_tasks_from_file(filename))[0]
    validated_task.perform()
    data = read_items_from_txt_file(validated_task.specifications.output_filename)
    start = datetime(*START_DATETIME)
    end = datetime(*END_DATETIME)
    for product in data:
        assert start <= SeviriIDParser.parse(product) < end
