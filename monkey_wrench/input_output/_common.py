import shutil
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from loguru import logger
from pydantic import DirectoryPath, FilePath, validate_call

from monkey_wrench.date_time import DateTimeParserBase
from monkey_wrench.generic import ListSetTuple, Pattern, apply_to_single_or_collection, type_
from monkey_wrench.input_output._models import DirectoryVisitor
from monkey_wrench.input_output._types import AbsolutePath

T = TypeVar("T")


@validate_call
def copy_files_between_directories(
        source_directory: AbsolutePath[DirectoryPath],
        destination_directory: AbsolutePath[DirectoryPath],
        pattern: Pattern | None = None,
) -> list[Path]:
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

    Returns:
        The list of filepaths that have been copied.
    """
    return DirectoryVisitor(
        parent_input_directory_path=source_directory,
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


@validate_call
def datetime_to_filename(prefix: str, datetime_object: datetime, extension: str = ".nc") -> Path:
    """Generate a CHIMP-compliant filename based on the datetime object and the given prefix.

    Args:
        prefix:
            A string with which the filename will start.
        datetime_object:
            The datetime object to retrieve the timestamp string from.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        A filename with the following format ``"<prefix>_<year><month><day>_<hour>_<minute><extension>"``.
    """
    chimp_timestamp_str = datetime_object.strftime("%Y%m%d_%H_%M")
    return Path(f"{prefix}_{chimp_timestamp_str}{extension}")


@validate_call
def __dispatch(
        prefix: str,
        single_item_or_list: datetime | str | ListSetTuple[datetime] | ListSetTuple[str],
        datetime_parser: type[DateTimeParserBase] | None = None,
        extension: str = ".nc"
) -> Path | list[Path]:
    """Dispatch the given input to its corresponding CHIMP-compliant filename function."""
    tp = type_(single_item_or_list)
    if tp is datetime:
        return apply_to_single_or_collection(lambda x: datetime_to_filename(prefix, x, extension), single_item_or_list)
    elif tp is str and datetime_parser is not None:
        return apply_to_single_or_collection(
            lambda x: datetime_to_filename(prefix, datetime_parser.parse(x), extension), single_item_or_list
        )
    else:
        raise TypeError(f"I do not know how to dispatch for type {tp}.")


@validate_call
def output_filename_from_datetime(
        datetime_objects: datetime | ListSetTuple[datetime], extension: str = ".nc"
) -> Path | ListSetTuple[Path]:
    """Generate (a) CHIMP-compliant output filename(s) based on (a) datetime object(s).

    Args:
        datetime_objects:
            Either a single datetime object , or a list/set/tuple of datetime objects.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        Depending on the input, either a single filename, or a list/set/tuple of filenames. The type of the
        output matches the type of the input in case of a list/set.tuple, e.g. a tuple of strings as input will result
        in a tuple of paths.

    Example:
        >>> output_filename_from_datetime(datetime(2020, 1, 1, 0, 12))
        PosixPath('chimp_20200101_00_12.nc')

        >>> output_filename_from_datetime(
        ...  [datetime(2020, 1, 1, 0, 12), datetime(2020, 3, 4, 2, 42)]
        ... )
        [PosixPath('chimp_20200101_00_12.nc'), PosixPath('chimp_20200304_02_42.nc')]
    """
    return __dispatch(
        "chimp",
        datetime_objects,
        None,
        extension
    )
