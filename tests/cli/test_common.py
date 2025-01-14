from collections import namedtuple
from unittest import mock

from monkey_wrench.cli import run
from monkey_wrench.task import InputFile
from tests.utils import cli_arguments

# ======================================================
### Tests for run()

def _run(empty_task_filepath):
    Task = namedtuple("Task", ["perform"])
    task = Task(perform=mock.Mock())

    func = dict(
        path="monkey_wrench.cli._common.read_tasks_from_file",
        arg=InputFile(input_filename=empty_task_filepath),
        return_value=[task, task],
    )

    with cli_arguments(empty_task_filepath):
        with mock.patch(func["path"], return_value=func["return_value"]) as read_tasks_from_file:
            run()
            read_tasks_from_file.assert_called_once_with(func["arg"])
            assert 2 == task.perform.call_count
