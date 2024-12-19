"""The module providing functionalities for multiprocessing."""

from multiprocessing import Pool
from pathlib import Path
from typing import Any, Callable

from monkey_wrench import input_output
from monkey_wrench.generic import IterableContainer


def run_multiple_processes(
        function: Callable,
        arguments: IterableContainer[Any],
        number_of_processes: int = 2,
        # Suppress Ruff linter rule S108 regarding insecure use of temporary directory.
        temp_directory: Path = Path("/tmp")  # noqa: S108
) -> list[Any]:
    """Call the provided function with different arguments in parallel.

    Args:
        function:
            The function to be called. The function must only accept a single argument and must not be a ``lambda``.
            In case you need a function with several input arguments, your function can accept all the arguments as a
            single input argument and then unpack, index, or iterate over them inside the function body.
            See the example below.
        arguments:
            An iterable of arguments that will be passed to the function.
        number_of_processes:
            Number of process to use. Defaults to ``2``.
        temp_directory:
            The temporary directory to use. Defaults to ``"/tmp"``. Default path might not be a good idea, especially
            when the space allocated for ``"/tmp"`` on the servers is limited.

    Returns:
        A list of returned results from the function in the same order as the given arguments.

    Example:
        >>> from monkey_wrench.process import run_multiple_processes
        >>> def add(x):  # Note that the function only accepts a single argument!
        ...   return x[0] ** x[1]  # We use indices to extract our desired arguments from the single input argument.
        ...
        >>> run_multiple_processes(add, [(1, 3), (2, 5)], number_of_processes=2)
        [1, 243]
    """
    with input_output.temp_directory(temp_directory):
        with Pool(processes=number_of_processes) as pool:
            results = pool.map(function, arguments)
    return results
