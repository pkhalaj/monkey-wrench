"""Module to define Pydantic models for paths specifications."""

from typing import Any

from pydantic import DirectoryPath, FilePath, NewPath, field_validator

from monkey_wrench.io_utils import AbsolutePath

from .base import Specifications


class OutputFile(Specifications):
    output_filename: AbsolutePath[NewPath]

    # noinspection PyNestedDecorators
    @field_validator("output_filename", mode="before")
    @classmethod
    def validate_filename_is_not_directory_like(cls, value: Any) -> Any:
        if str(value).endswith("/"):
            raise ValueError("Output filename cannot end with a '/'")
        return value


class InputFile(Specifications):
    input_filename: AbsolutePath[FilePath]


class InputDirectory(Specifications):
    input_directory: AbsolutePath[DirectoryPath]


class OutputDirectory(Specifications):
    output_directory: AbsolutePath[DirectoryPath]
