"""The module providing the main executable function for the CLI."""

from monkey_wrench.cli._models import CommandLineArguments
from monkey_wrench.error import pretty_error_logs
from monkey_wrench.task import read_tasks_from_file


@pretty_error_logs
def run() -> None:
    """The main entrypoint, when **Monkey Wrench** is invoked from the CLI.

    It uses the task file which has been provided via the CLI. It then goes through each task, parses it, and
    performs it. The order of the tasks matches their order in the task file.

    Example:

        .. code-block:: bash

            # Note that the filepath must end in `.yaml` or `.yml`.
            monkey-wrench <task_file_path>
    """
    for task in read_tasks_from_file(CommandLineArguments().task_filepath):
        task.perform()
