from pathlib import PosixPath

import pytest
from pydantic import ValidationError

from monkey_wrench.cli import CommandLineArguments
from monkey_wrench.input_output import InputFile
from tests.utils import cli_arguments

# ======================================================
### Tests for CommandLineArguments()

@pytest.mark.parametrize(("args", "msg"), [
    ([], "single"),
    ([1, 2], "single"),
    (["task.yaml"], "point to a file"),
    (["task.yml"], "point to a file"),
    (["task"], "point to a file"),
])
def test_CommandLineArguments_raise(args, msg):
    with pytest.raises(ValidationError, match=msg):
        with cli_arguments(*args):
            CommandLineArguments()


def test_CommandLineArguments(empty_task_filepath):
    with cli_arguments(empty_task_filepath):
        filepath = CommandLineArguments().task_filepath
        assert filepath == InputFile(input_filename=empty_task_filepath).input_filename
        assert isinstance(filepath, PosixPath)
        assert filepath.exists()
