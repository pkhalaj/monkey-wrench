from typing import Any

import yaml
from pydantic import BaseModel, validate_call

from .models.specifications.paths import InputFile
from .models.tasks.files import FilesTask
from .models.tasks.ids import IdsTask

Task = FilesTask | IdsTask


class _Task(BaseModel):
    data: Task


@validate_call
def read_task_from_file(filename: Any) -> Task:
    """Read and parse a task from the given ``.yaml`` file."""
    filename = InputFile(input_filename=filename).input_filename
    with open(filename, "r") as f:
        return _Task(data=yaml.safe_load(f)).data
