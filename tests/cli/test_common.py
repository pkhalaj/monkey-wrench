from collections import namedtuple
from unittest import mock

from monkey_wrench.cli import run
from monkey_wrench.input_output import ExistingInputFile
from tests.utils import cli_arguments

# ======================================================
### Tests for run()

def test_run(empty_task_filepath):
    Task = namedtuple("Task", ["perform"])
    task = Task(perform=mock.Mock())

    func = dict(
        path="monkey_wrench.cli._common.read_tasks_from_file",
        arg=ExistingInputFile(input_filepath=empty_task_filepath).input_filepath,
        return_value=[task, task],
    )

    with cli_arguments(empty_task_filepath):
        with mock.patch(func["path"], return_value=func["return_value"]) as read_tasks_from_file:
            run()
            read_tasks_from_file.assert_called_once_with(func["arg"])
            assert task.perform.call_count == 2
