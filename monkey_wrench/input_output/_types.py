from pathlib import Path
from typing import Literal, TypeVar

from pydantic import AfterValidator, DirectoryPath, FilePath, NewPath
from typing_extensions import Annotated


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
