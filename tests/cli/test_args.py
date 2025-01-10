from pathlib import Path

import pytest
from cli import CommandLineArguments
from pydantic import ValidationError

from tests.utils import CLIArguments, make_yaml_file


@pytest.mark.parametrize(("args", "msg"), [
    ([], "single"),
    (["task"], "end in"),
    (["task.txt"], "end in"),
    ([1, 2], "single"),
    (["task.yaml"], "point to a file"),
    (["task.yml"], "point to a file")
])
def test_command_line_arguments_fail(args, msg):
    with pytest.raises(ValidationError, match=msg):
        with CLIArguments(*args):
            CommandLineArguments()


def test_command_line_arguments_success(temp_dir):
    task_filepath = Path(temp_dir, "task.yaml")
    make_yaml_file(task_filepath, {})
    with CLIArguments(str(task_filepath)):
        CommandLineArguments()
