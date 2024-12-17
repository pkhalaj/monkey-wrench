"""The module to provide functionalities for process and multiprocessing."""

from multiprocessing import Pool
from pathlib import Path
from typing import Any, Callable, Generator

from monkey_wrench import input_output


def run_multiple_processes(
        function: Callable,
        arguments: Generator | list,
        number_of_processes: int = 2,
        # Suppress Ruff linter rule S108 regarding insecure use of temporary directory.
        temp_directory: Path = Path("/tmp")  # noqa: S108
) -> list[Any]:
    """Call the provided function with different arguments in parallel.

    Args:
        function:
            The function to be called.
        arguments:
            A generator which yields the arguments passed to the function.
        number_of_processes:
            Number of process to use. Defaults to ``2``.
        temp_directory:
            The temporary directory to use. Defaults to ``"/tmp"``. Default path might not be a good idea, especially
            when the space allocated for ``"/tmp"`` on the servers is limited.

    Returns:
        A list of returned results from the function in the same order as the given arguments.
    """
    with input_output.temp_directory(temp_directory):
        with Pool(processes=number_of_processes) as pool:
            results = pool.map(function, arguments)
    return results
