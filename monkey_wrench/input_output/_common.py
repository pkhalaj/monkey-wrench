import shutil
from datetime import datetime
from pathlib import Path
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
        input_directory=source_directory,
        callback=lambda f: copy_single_file_to_directory(destination_directory, f),
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


@validate_call
@validate_call
def create_datetime_directory(
        datetime_object: datetime,
        format_string: str = "%Y/%m/%d",
        parent: AbsolutePath[DirectoryPath] = Path("."),
        remove_if_exists: bool = False,
        dry_run: bool = False
) -> Path:
    """Create a directory based on the datetime object.

    Args:
        datetime_object:
            The datetime object to create the directory for.
        format_string:
            The format string to create subdirectories from the datetime object. Defaults to ``"%Y/%m/%d"``.
        parent:
            The parent directory inside which the directory will be created. Defaults to ``"."``.
        remove_if_exists:
            A boolean indicating whether to remove the directory (recursively) if it already exists.
        dry_run:
            If ``True``, nothing will be created or removed and only the directory path will be returned.
            Defaults to ``False``, meaning that changes will be made to the disk.

    Returns:
        The full path of the (created) directory.

    Example:
        >>> path = create_datetime_directory(datetime(2022, 3, 12), format_string="%Y/%m/%d", parent=Path.home())
        >>> expected_path = Path.home() / Path("2022/03/12")
        >>> expected_path.exists()
        True
        >>> expected_path == path
        True
    """
    dir_path = parent / Path(datetime_object.strftime(format_string))
    if not dry_run:
        if dir_path.exists() and remove_if_exists:
            dir_path.unlink()
        dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
