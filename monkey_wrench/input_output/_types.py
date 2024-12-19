from enum import Enum
from typing import TypeVar

from pydantic import AfterValidator, DirectoryPath, FilePath, NewPath
from typing_extensions import Annotated


class WriteMode(Enum):
    """An enum for different write modes."""
    append = "a"
    overwrite = "w"


T = TypeVar("T", DirectoryPath, NewPath, FilePath)
AbsolutePath = Annotated[T, AfterValidator(lambda x: x.absolute())]
"""Type annotation and Pydantic validator to represent (convert to) an absolute path."""

Pattern = str | list[str] | None
"""Type alias for a string or a list of strings that will be used as a pattern to search in other strings."""
