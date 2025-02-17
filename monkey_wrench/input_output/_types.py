import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Literal, Self, TypeVar

from pydantic import AfterValidator, DirectoryPath, FilePath, NewPath, model_validator
from typing_extensions import Annotated

from monkey_wrench.generic import Model


def ensure_path_does_not_end_with_slash(path: Path) -> Path:
    """Check that the path does not end with a slash, and therefore it does not point to a directory."""
    if str(path).endswith("/"):
        raise ValueError("A file path cannot end with a slash")
    return path


PathType = TypeVar("PathType", DirectoryPath, NewPath, FilePath)
AbsolutePath = Annotated[PathType, AfterValidator(lambda path: path.resolve().absolute())]
"""Type annotation and Pydantic validator to represent (convert to) an absolute and normalized path."""

ExistingFilePath = Annotated[AbsolutePath[FilePath], AfterValidator(ensure_path_does_not_end_with_slash)]
NewFilePath = Annotated[AbsolutePath[NewPath], AfterValidator(ensure_path_does_not_end_with_slash)]

ExistingDirectoryPath = AbsolutePath[DirectoryPath]
NewDirectoryPath = AbsolutePath[NewPath]

WriteMode = Literal["w", "a"]
"""Either ``"a"`` for appending to, or ``"w"`` for overwriting an existing file."""


class TempDirectory(Model):
    """Pydantic model for a temporary directory, including a context manager."""

    temporary_directory: ExistingDirectoryPath
    """The path to an existing directory, which will be used as the top-level temporary directory.

    Note:
        This directory will be used as a parent directory for subsequent temporary directories. As a result, it will not
        be removed. However, the child temporary directories will always be removed.

    Note:
        If it is not set (i.e. it is ``None``), it takes on a value according to the following order of priority:
            1- The value of the ``TMPDIR`` environment variable.
            2- ``/tmp/``.
    """

    @model_validator(mode="before")
    def validate_temporary_directory(self) -> Self:
        """Return the path to the top-level temporary directory according to the priority rules."""
        # The following is the default temporary directory that will be used by the OS anyway.
        # Therefore, we suppress Ruff linter rule S108.
        if not self.get("temporary_directory", None):
            self["temporary_directory"] = Path(os.environ.get("TMPDIR", "/tmp/"))  # noqa: S108
        return self

    @contextmanager
    def context(self) -> Generator[Path, None, None]:
        """Context manager to create a temporary directory and set the global temporary directory to the specified path.

        Note:
            The temporary directory created by this context manager will reside inside
            :attr:`TempDirectory.temporary_directory`.

        Note:
            The reason to set the global temporary directory is to ensure that any other inner functions or context
            managers that might invoke ``tempfile.TemporaryDirectory()`` also use the given global temporary directory.

        Yields:
            The full path of the (created) temporary directory.
        """
        _default_tempdir = tempfile.gettempdir()
        try:
            with tempfile.TemporaryDirectory(dir=self.temporary_directory) as _dir:
                tempfile.tempdir = _dir
                yield Path(_dir)
        finally:
            tempfile.tempdir = _default_tempdir
