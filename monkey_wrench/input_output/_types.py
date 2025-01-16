"""The module providing common types for the ``input_output`` package."""

from typing import TypeVar

from pydantic import AfterValidator, DirectoryPath, FilePath, NewPath
from typing_extensions import Annotated

T = TypeVar("T", DirectoryPath, NewPath, FilePath)
AbsolutePath = Annotated[T, AfterValidator(lambda x: x.absolute())]
"""Type annotation and Pydantic validator to represent (convert to) an absolute path."""
