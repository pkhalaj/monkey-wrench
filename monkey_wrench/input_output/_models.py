from typing import Any

from pydantic import DirectoryPath, FilePath, NewPath, NonNegativeFloat, PositiveInt, field_validator

from monkey_wrench.generic import Specifications
from monkey_wrench.input_output._types import AbsolutePath


class OutputFile(Specifications):
    output_filename: AbsolutePath[NewPath]

    # noinspection PyNestedDecorators
    @field_validator("output_filename", mode="before")
    @classmethod
    def validate_filename_is_not_directory_like(cls, value: Any) -> Any:
        if str(value).endswith("/"):
            raise ValueError("Output filename cannot end with a '/'")
        return value


class ModelFile(Specifications):
    model_filename: AbsolutePath[FilePath]


class InputFile(Specifications):
    input_filename: AbsolutePath[FilePath]


class InputDirectory(Specifications):
    input_directory: AbsolutePath[DirectoryPath]


class OutputDirectory(Specifications):
    output_directory: AbsolutePath[DirectoryPath]


class TempDirectory(Specifications):
    temp_directory: AbsolutePath[DirectoryPath]


class FileSize(Specifications):
    nominal_size: PositiveInt
    tolerance: NonNegativeFloat = 0.01
