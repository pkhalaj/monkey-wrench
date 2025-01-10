from collections import namedtuple
from unittest import mock

from monkey_wrench.cli import run
from monkey_wrench.task import InputFile
from tests.utils import CLIArguments, noop


def test_run(empty_task_filepath):
    Task = namedtuple("Task", ["perform"])

    func = dict(
        path="monkey_wrench.cli._common.read_tasks_from_file",
        arg=InputFile(input_filename=empty_task_filepath),
        return_value=[Task(perform=noop)]
    )

    with CLIArguments(empty_task_filepath):
        with mock.patch(func["path"], return_value=func["return_value"]) as read_tasks_from_file:
            run()
            read_tasks_from_file.assert_called_once_with(func["arg"])
