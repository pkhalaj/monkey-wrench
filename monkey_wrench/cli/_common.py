from monkey_wrench.cli._models import CommandLineArguments
from monkey_wrench.error import pretty_error_logs
from monkey_wrench.task.common import read_tasks_from_file


@pretty_error_logs
def run() -> None:
    """The main entrypoint, when **Monkey Wrench** is invoked from the CLI.

    It uses the task file which has been provided via the CLI. It then goes through each task, parses it, and
    performs it. The order at which the tasks run, matches their order in the task file.

    Example:

        .. code-block:: bash
            :caption: Running **Monkey Wrench** in the task runner mode

            # The task file must be a valid YAML file.
            $ monkey-wrench <task_file_path>
    """
    for task in read_tasks_from_file(CommandLineArguments().task_file_path):
        task.perform()
