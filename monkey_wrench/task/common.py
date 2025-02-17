"""The module which defines a function to read the tasks from a file."""

from typing import Generator

import yaml
from pydantic import BaseModel, validate_call

from monkey_wrench.input_output import ExistingFilePath
from monkey_wrench.task.files import FilesTask
from monkey_wrench.task.ids import IdsTask

Task = IdsTask | FilesTask


class _Task(BaseModel):
    data: Task


@validate_call
def read_tasks_from_file(filepath: ExistingFilePath) -> Generator[Task, None, None]:
    """Read and parse task(s) from the given ``.yaml`` file.

    Args:
        filepath:
            The path of the YAML file to read the task(s) from. In case of multiple tasks in the same file, different
            tasks must be separated by three dashes ``"---"``. In the language of YAML files, each task is essentially
            a document.

    Yields:
        A generator yielding the task(s) from the given YAML file.
    """
    with open(filepath, "r") as f:
        for document in yaml.safe_load_all(f):
            yield _Task(data=document).data
