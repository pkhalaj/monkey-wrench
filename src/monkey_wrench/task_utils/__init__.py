from typing import Any, Generator

import yaml
from pydantic import BaseModel, validate_call

from .models.specifications.paths import InputFile
from .models.tasks.files import FilesTask
from .models.tasks.ids import IdsTask

Task = FilesTask | IdsTask


class _Task(BaseModel):
    data: Task


@validate_call
def read_tasks_from_file(filename: Any) -> Generator[Task, None, None]:
    """Read and parse task(s) from the given ``.yaml`` file.

    Args:
        filename:
            The name of the ``.yaml`` file to read the task(s) from. In case of multiple tasks in the same file,
            different tasks must be separated by three dashes ``"---"``. In the language of YAML files, each task is
            essentially a document.

    Yields:
        A generator yielding the task(s) from the given ``.yaml`` file.
    """
    filename = InputFile(input_filename=filename).input_filename
    with open(filename, "r") as f:
        for document in yaml.safe_load_all(f):
            yield _Task(data=document).data
