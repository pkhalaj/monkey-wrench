import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Literal, Self, TypeVar

from pydantic import AfterValidator, DirectoryPath, FilePath, NewPath, model_validator
from typing_extensions import Annotated

from monkey_wrench.generic import Model


def ensure_path_does_not_end_with_slash(path: Path) -> Path:
    """Check that the path does not end with a slash, and therefore, it does not point to a directory."""
    if str(path).endswith("/") or str(path).endswith("\\"):
        raise ValueError("A file path cannot end with a slash!")
    return path


PathType = TypeVar("PathType", DirectoryPath, NewPath, FilePath)
AbsolutePath = Annotated[PathType, AfterValidator(lambda path: path.resolve().absolute())]
"""Type annotation and Pydantic validator to represent (convert to) an absolute and normalized path."""

ExistingFilePath = Annotated[AbsolutePath[FilePath], AfterValidator(ensure_path_does_not_end_with_slash)]
"""Type annotation and Pydantic validator for an existing file path.

Note:
    After the validation, the path will be normalized and made into an absolute path.

Warning:
    The path must not end with `/` or ``\\``.
"""

NewFilePath = Annotated[AbsolutePath[NewPath], AfterValidator(ensure_path_does_not_end_with_slash)]
"""Type annotation and Pydantic validator for a non-existing file path.

Note:
    After the validation, the path will be normalized and made into an absolute path.

Warning:
    The path must not end with `/` or ``\\``.
"""

ExistingDirectoryPath = AbsolutePath[DirectoryPath]
"""Type annotation and Pydantic validator for an existing directory path.

Note:
    After the validation, the path will be normalized and made into an absolute path.

Note:
    The path can optionally end with `/` or ``\\``.
"""

NewDirectoryPath = AbsolutePath[NewPath]
"""Type annotation and Pydantic validator for a non-existing directory path.

Note:
    After the validation, the path will be normalized and made into an absolute path.

Note:
    The path can optionally end with `/` or ``\\``.
"""

OpenMode = Literal["w", "a"]
"""Type alias for the union of a literal ``"a"`` (for appending to), or ``"w"`` (for overwriting an existing file).

This only concerns ASCII (text) files.
"""


class TempDirectory(Model):
    """Pydantic model for a temporary directory, including a context manager."""

    temp_directory_path: ExistingDirectoryPath | NewDirectoryPath
    """The path to the directory, which will be used as the top-level temporary directory.

    Note:
        If the directory does not exist, it will be created. Once created, the top-level temporary directory will not be
        deleted by **Monkey Wrench**.

    Note:
        This directory will be used as a parent directory for subsequent (child) temporary directories. As a result, it
        will not be removed or cleaned up. However, the child temporary directories will always be removed and
        cleaned up.

    Note:
        If it is not set (i.e. it is ``None``), it takes on a value according to the following order of priority:

            1- The value of the ``TMPDIR`` environment variable.

            2- ``/tmp/``.
    """

    @model_validator(mode="before")
    def validate_temporary_directory_default_values(cls, data: Any) -> Any:
        """Return the path to the top-level temporary directory according to the priority rules."""
        # The following is the default temporary directory that will be used by the OS anyway.
        # Therefore, we suppress Ruff linter rule S108.
        if not data.get("temp_directory_path"):
            data["temp_directory_path"] = Path(os.environ.get("TMPDIR", "/tmp/"))  # noqa: S108
        return data

    @model_validator(mode="after")
    def validate_temporary_directory_exists(self) -> Self:  # noqa: N804
        """Create the temporary directory if it does not exist."""
        if not self.temp_directory_path.exists():
            self.temp_directory_path.mkdir(parents=True, exist_ok=True)
        return self

    @contextmanager
    def temp_dir_context_manager(self) -> Generator[Path, None, None]:
        """Context manager to create a temporary directory and also set the global temporary directory to the same path.

        Note:
            The temporary directory created by this context manager will reside inside
            :attr:`TempDirectory.temp_directory_path`.

        Note:
            The reason to set the global temporary directory is to ensure that any other inner functions or context
            managers that might invoke ``tempfile.TemporaryDirectory()`` also use the given global temporary directory.

        Yields:
            The full path of the (created) temporary directory.
        """
        _default_tempdir = tempfile.gettempdir()
        try:
            with tempfile.TemporaryDirectory(dir=self.temp_directory_path) as _dir:
                tempfile.tempdir = _dir
                yield Path(_dir)
        finally:
            tempfile.tempdir = _default_tempdir
