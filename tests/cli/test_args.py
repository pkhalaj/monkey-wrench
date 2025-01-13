import pytest
from pydantic import ValidationError

from monkey_wrench.cli import CommandLineArguments
from tests.utils import cli_arguments


@pytest.mark.parametrize(("args", "msg"), [
    ([], "single"),
    (["task"], "end in"),
    (["task.txt"], "end in"),
    ([1, 2], "single"),
    (["task.yaml"], "point to a file"),
    (["task.yml"], "point to a file")
])
def _CommandLineArguments_raise(args, msg):
    with pytest.raises(ValidationError, match=msg):
        with cli_arguments(*args):
            CommandLineArguments()


def _CommandLineArguments(empty_task_filepath):
    with cli_arguments(empty_task_filepath):
        CommandLineArguments()
