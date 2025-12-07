"""The module providing functionalities for multiprocessing."""

from multiprocessing import get_context
from typing import Callable, TypeVar

from pydantic import NonNegativeInt

from monkey_wrench.generic import ListSetTuple, Model

T = TypeVar("T")
R = TypeVar("R")


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

    def run(self, function: Callable[[T], R], arguments: ListSetTuple[T]) -> None:
        """Similar to :func:`run_with_results`, but does not return anything.

        If the function returns anything, it will be discarded!
        """
        ctx = get_context("spawn")
        arguments = list(arguments)
        for index in range(0, len(arguments), self.number_of_processes):
            procs = []
            for arg in arguments[index: index + self.number_of_processes]:
                proc = ctx.Process(target=function, args=(arg,))
                procs.append(proc)
                proc.start()
            for proc in procs:
                proc.join()
            for proc in procs:
                proc.close()
