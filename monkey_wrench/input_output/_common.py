import shutil
from typing import TypeVar

from loguru import logger
from pydantic import DirectoryPath, FilePath, validate_call

from monkey_wrench.generic import Pattern
from monkey_wrench.input_output._models import DirectoryVisitor
from monkey_wrench.input_output._types import AbsolutePath

T = TypeVar("T")


@validate_call
def copy_files_between_directories(
        source_directory: AbsolutePath[DirectoryPath],
        destination_directory: AbsolutePath[DirectoryPath],
        pattern: Pattern | None = None,
) -> None:
    """Copy (top-level) files whose names include the pattern from one directory to another.

    Warning:
        The copying is not performed recursively. Only the top-level files are copied.

    Args:
        source_directory:
            The source directory to copy files from.
        destination_directory:
            The destination directory to copy files to.
        pattern:
            The pattern to filter the files.
    """
    DirectoryVisitor(
        parent_directory=source_directory,
        visitor_callback=lambda f: copy_single_file_to_directory(destination_directory, f),
        recursive=False,
        **(pattern.model_dump() if pattern is not None else {})
    ).visit()


@validate_call
def copy_single_file_to_directory(
        destination_directory: AbsolutePath[DirectoryPath], filepath: AbsolutePath[FilePath]
) -> None:
    """Copy a single file with the given path to another destination directory.

    Args:
        destination_directory:
            The destination directory to copy the given file to.
        filepath:
            The path of the file that needs to be copied.
    """
    destination_filepath = destination_directory / filepath.name
    logger.info(f"Copying {filepath} to {destination_filepath}")
    shutil.copy(filepath, destination_filepath)
