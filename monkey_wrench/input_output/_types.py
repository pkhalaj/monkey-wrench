import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, TypeVar

from pydantic import AfterValidator, DirectoryPath, FilePath, NewPath
from typing_extensions import Annotated

from monkey_wrench.generic import Specifications

T = TypeVar("T", DirectoryPath, NewPath, FilePath)
AbsolutePath = Annotated[T, AfterValidator(lambda x: x.absolute())]
"""Type annotation and Pydantic validator to represent (convert to) an absolute path."""


class TempDirectory(Specifications):
    """Pydantic for a temporary directory."""
    temp_directory: AbsolutePath[DirectoryPath] | None = None
    """The path to the temporary directory.

    If it is not set, it takes on a value according to the following order of priority:
        1- The value of the ``TMPDIR`` environment variable.
        2- ``/tmp/``.
    """

    def get_temp_directory(self) -> AbsolutePath[DirectoryPath]:
        """Return the path to the temporary directory."""
        # The following is only the default temp directory that will be used by the OS anyway.
        # Therefore, we suppress Ruff linter rule S108.
        if self.temp_directory is None:
            self.temp_directory = Path(os.environ.get("TMPDIR", "/tmp/"))  # noqa: S108
        return self.temp_directory

    @contextmanager
    def context(self) -> Generator[Path, None, None]:
        """Create a temporary directory and set the global temporary directory to the given path.

        Note:
            The reason to set the global temporary directory is to ensure that any other inner functions or context
            managers that might invoke ``tempfile.TemporaryDirectory()`` also use the given global temporary directory.

        Yields:
            The full path of the (created) temporary directory.
        """
        _default_tempdir = tempfile.gettempdir()
        try:
            with tempfile.TemporaryDirectory(dir=self.get_temp_directory()) as _dir:
                tempfile.tempdir = _dir
                yield Path(_dir)
        finally:
            tempfile.tempdir = _default_tempdir
