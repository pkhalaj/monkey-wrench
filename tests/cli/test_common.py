from collections import namedtuple
from unittest import mock
from unittest.mock import MagicMock

from monkey_wrench.cli import run
from monkey_wrench.task import InputFile
from tests.utils import CLIArguments


def test_run(empty_task_filepath):
    Task = namedtuple("Task", ["perform"])
    task = Task(perform=MagicMock())

    func = dict(
        path="monkey_wrench.cli._common.read_tasks_from_file",
        arg=InputFile(input_filename=empty_task_filepath),
        return_value=[task, task],
    )

    with CLIArguments(empty_task_filepath):
        with mock.patch(func["path"], return_value=func["return_value"]) as read_tasks_from_file:
            run()
            read_tasks_from_file.assert_called_once_with(func["arg"])
            assert 2 == task.perform.call_count
