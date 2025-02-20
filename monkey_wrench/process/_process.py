"""The module providing functionalities for multiprocessing."""

import tempfile
from multiprocessing import get_context
from pathlib import Path
from typing import Callable, TypeVar

from pydantic import NonNegativeInt

from monkey_wrench.generic import ListSetTuple, Model
from monkey_wrench.input_output._types import TempDirectory

T = TypeVar("T")
R = TypeVar("R")


def _wrap_function_no_return(function: Callable[[T], R], argument: T, temporary_directory_path: Path) -> None:
    """Wrap the function by setting the global temporary directory.

    The function is to be run in a separate **spawned** (and not forked) process!
    """
    tempfile.tempdir = str(temporary_directory_path)
    function(argument)


class MultiProcess(Model):
    """Pydantic model for multiprocessing.

    Example:

        .. code-block:: python

            def power(x):            # Note that the function only accepts a single argument!
                print(x[0] ** x[1])  # We use indices to extract our desired arguments from the single input argument.

            MultiProcess(number_of_processes=2).run(power, [(1, 3), (2, 5)])
    """

    number_of_processes: NonNegativeInt = 1
    """Number of process to use. Defaults to ``1``.

    A value of ``1`` disables multiprocessing. This is useful for e.g. testing purposes.
    """

    def run_with_results(self, function: Callable[[T], R], arguments: ListSetTuple[T]) -> list[R]:
        """Call the provided function with different arguments using multiple processes.

        Args:
            function:
                The function to be called. It must only accept a single argument and must not be a ``lambda``. In case
                you need a function with several input arguments, your function can accept single a tuple which packs
                all the arguments. You can then unpack, index, or iterate over the input, inside the function body.
                See the example.

            arguments:
                An iterable (list/set/tuple) of arguments that will be passed to the function.

        Returns:
            A list of returned results from the function in the same order as the given arguments (if not a set).
        """
        ctx = get_context("spawn")

        if self.number_of_processes == 1:
            return [function(arg) for arg in arguments]

        with ctx.Pool(processes=self.number_of_processes) as pool:
            results = pool.map(function, arguments)

        return results

    def run(
            self, function: Callable[[T], R], arguments: ListSetTuple[T], temp_directory_path: Path | None = None
    ) -> None:
        """Similar to :func:`run_with_results`, but does not return anything.

        If the function returns anything, it will be thrown away!
        """
        ctx = get_context("spawn")
        arguments = list(arguments)
        temp_directory = TempDirectory(temp_directory_path=temp_directory_path)
        for index in range(0, len(arguments), self.number_of_processes):
            with temp_directory.context_manager() as tmp_dir:
                procs = []
                for arg in arguments[index: index + self.number_of_processes]:
                    proc = ctx.Process(target=_wrap_function_no_return, args=(function, arg, tmp_dir))
                    procs.append(proc)
                    proc.start()
                for proc in procs:
                    proc.join()
                for proc in procs:
                    proc.close()
