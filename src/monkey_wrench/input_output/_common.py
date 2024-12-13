"""The module which defines functions to handle IO operations and manipulations of files and filenames."""

import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generator, Literal, TypeVar

import requests
from loguru import logger
from pydantic import AfterValidator, DirectoryPath, FilePath, NewPath, NonNegativeInt, PositiveInt, validate_call
from typing_extensions import Annotated

from monkey_wrench.date_time import Order
from monkey_wrench.process import run_multiple_processes
from monkey_wrench.query import Results

T = TypeVar("T", DirectoryPath, NewPath, FilePath)
AbsolutePath = Annotated[T, AfterValidator(lambda x: x.absolute())]
"""Type annotation and Pydantic validator to represent (convert to) an absolute path."""

Pattern = str | list[str] | None
"""Type alias for a string or a list of strings that will be used as a pattern to search in other strings."""


@validate_call
def pattern_exists(item: str, pattern: Pattern = None, match_all: bool = True, case_sensitive: bool = True) -> bool:
    """Check if a string or a list of strings exists in the given item.

    Args:
        item:
            The string in which the pattern(s) will be looked for.
        pattern:
            The pattern(s) to look for. It can be either a single string, a list of strings, or  ``None.``.
            Defaults to ``None``, which means that the function returns ``True``.
        match_all:
            A boolean indicating whether to match all pattern(s) in case of a pattern list. Defaults to ``True``.
            When it is set to ``False``, only one match suffices. In the case of a single string this parameter does
            not have any effect.
        case_sensitive:
            A boolean indicating whether to perform a case-sensitive match. Defaults to ``True``.

    Returns:
        A boolean indicating whether all or any (depending on ``match_all``) of the pattern(s) exist(s) in the given
        item.
    """
    if pattern is None:
        return True

    if not isinstance(pattern, list):
        pattern = [pattern]

    if not case_sensitive:
        item = item.lower()
        pattern = [i.lower() for i in pattern]

    func = all if match_all is True else any
    return func(i in item for i in pattern)


@validate_call
def collect_files_in_directory(
        directory: AbsolutePath[DirectoryPath],
        callback: Callable | None = None,
        pattern: Pattern = None,
        order: Order = Order.increasing,
        **kwargs
) -> list[Path]:
    """Get the list of all files in a directory and all of its subdirectories.

    The function visits the directory tree recursively.

    Args:
        directory:
            The top-level directory to collect the files from.
        callback:
            A function that will be called everytime a match is found for a file. Defaults to ``None``.
        pattern:
            If given, it will be used to filter files, i.e. a file must have the pattern(s) as (a) substring(s) in its
            name. Defaults to ``None`` which means no filtering. See :func:`pattern_exists` for more information.
        order:
            Either :obj:`~monkey_wrench.date_time.Order.decreasing` or
            :obj:`~monkey_wrench.date_time.Order.increasing`. Defaults to
            :obj:`~monkey_wrench.date_time.Order.increasing`.
        kwargs:
            Other keyword arguments to pass to :func:`pattern_exists`.

    Returns:
        A sorted flat list of all files in the given directory.
    """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if pattern_exists(file, pattern, **kwargs):
                filename = Path(root, file)
                file_list.append(filename)
                if callback is not None:
                    callback(filename)
    return sorted(file_list, reverse=True if order == Order.decreasing else False)


@validate_call
def copy_files_between_directories(
        source_directory: AbsolutePath[DirectoryPath],
        destination_directory: AbsolutePath[DirectoryPath],
        pattern: Pattern = None,
        **kwargs
) -> None:
    """Copy files that match the pattern from one directory to another.

    Args:
        source_directory:
            The source directory to copy files from.
        destination_directory:
            The destination directory to copy files to.
        pattern:
            The pattern to filter the files.
        kwargs:
            Other keyword arguments that will be directly passed to :func:`pattern_exists`.
    """
    files = collect_files_in_directory(source_directory, pattern=pattern, **kwargs)
    for file in files:
        destination_file = destination_directory / file.name
        logger.info(f"copying {file} to {destination_file}")
        shutil.copy(file, destination_file)


@validate_call
def write_items_to_txt_file(
        items: list | Generator, items_list_filename: AbsolutePath[FilePath] | AbsolutePath[NewPath],
        write_mode: Literal["a", "w"] = "w"
) -> NonNegativeInt:
    """Write items from a list to a text file, with one item per line.

    Examples of items are product IDs.

    This function opens a text file in write mode and writes each item from the provided iterable to the file. It
    catches any potential errors during the writing process, and logs a warning.

    Args:
        items:
            An iterable of items to be written to the file.
        items_list_filename:
            The path to the (text) file where the items will be written.
        write_mode:
            Either "a" for "append" or "w" for "overwrite". Defaults to "w".

    Returns:
        The number of items that are written to the file successfully.
    """
    number_of_items = 0
    with open(items_list_filename, write_mode) as f:
        for item in items:
            try:
                f.write(f"{item}\n")
                number_of_items += 1
            except requests.exceptions.ConnectionError as error:
                logger.warning(f"Error related to the connection: {error}")
            except requests.exceptions.RequestException as error:
                logger.warning(f"Error related to the request: {error}")
            except Exception as error:
                logger.warning(f"Unexpected error: {error}")
    return number_of_items


@validate_call
def write_items_to_txt_file_in_batches(
        batches: Results, items_list_filename: AbsolutePath[FilePath] | AbsolutePath[NewPath]
) -> NonNegativeInt:
    """Similar to :func:`write_items_to_txt_file`, but assumes that the input is in batches."""
    with open(items_list_filename, mode="w"):
        pass
    number_of_items = 0
    for batch, _ in batches:
        number_of_items += write_items_to_txt_file(batch, items_list_filename, write_mode="a")
    return number_of_items


@validate_call
def read_items_from_txt_file(
        items_list_filename: AbsolutePath[FilePath], transform_function: Callable | None = None
) -> list[str]:
    """Get the list of items from a text file, assuming each line corresponds to a single item.

    Examples of items are product IDs.

    Warning:
        This function does not check whether the items are valid or not.

    Args:
        items_list_filename:
            The path to the (text) file containing the list of items.

        transform_function:
            If given, each item in the list will be first transformed according to the function before being
            appended to the list and returned. Defaults to ``None``, which means no transformation is performed and
            items will be returned as they are.

    Returns:
        A list of strings, where each string is an item.
    """
    with open(items_list_filename, "r") as f:
        items = [line.strip() for line in f.readlines()]
    if transform_function:
        return [transform_function(i) for i in items]
    return items


@validate_call
def create_datetime_directory(
        datetime_object: datetime,
        format_string: str = "%Y/%m/%d",
        parent: AbsolutePath[DirectoryPath] = Path("."),
        remove_if_exists=False,
        dry_run=False
) -> Path:
    """Create a directory based on the datetime object.

    Args:
        datetime_object:
            The datetime object to create the directory for.
        format_string:
            The format string to create subdirectories from the datetime object. Defaults to "%Y/%m/%d".
        parent:
            The parent directory inside which the directory will be created. Defaults to ".".
        remove_if_exists:
            A boolean indicating whether to remove the directory if it already exists.
        dry_run:
            If ``True``, nothing will be created or removed and only the directory path will be returned.
            Defaults to ``False``, meaning that changes will be made.

    Returns:
        The full path of the (created) directory.

    Example:
        >>> from datetime import datetime
        >>> from pathlib import Path
        >>> from monkey_wrench.input_output import create_datetime_directory
        >>> home = Path.home()
        >>> path = create_datetime_directory(datetime(2022, 3, 12), format_string="%Y/%m/%d", parent=home)
        >>> expected_path = home / Path("2022/03/12")
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


@contextmanager
@validate_call
def temp_directory(directory: AbsolutePath[DirectoryPath]) -> Path:
    """Create a temporary directory and set the global temporary directory to the given path.

    Note:
        The reason to set the global temporary directory is to ensure that any other inner function that might invoke
        ``tempfile.TemporaryDirectory()`` also uses the given global temporary directory.

    Yields:
        The full path of the (created) temporary directory.
    """
    _default_tempdir = tempfile.gettempdir()
    try:
        with tempfile.TemporaryDirectory(dir=directory) as _dir:
            tempfile.tempdir = _dir
            yield Path(_dir)
    finally:
        tempfile.tempdir = _default_tempdir


@validate_call
def compare_files_against_reference(
        files: list[Path],
        reference_list: list[Any] | None = None,
        transform_function: Callable | None = None,
        nominal_size: int | None = None,
        tolerance: float = 0.01,
        number_of_processes: PositiveInt = 20,
) -> tuple[set | None, set | None]:
    """Compare a list of files against a reference list of items and report missing and corrupted files.

    Args:
        files:
            The list of files to perform the check on.
        reference_list:
            The reference list of items to compare against. Defaults to ``None`` which means the search for missing
            files will not be performed.
        transform_function:
            A function to transform the files into new objects before comparing them against the reference. This can be
            e.g. a :func:`~monkey_wrench.date_time.DateTimeParser.parse` function to make datetime objects out of
            files. Defaults to ``None`` which means no transformation is performed and the files list and the reference
            list are compared as they are.
        nominal_size:
            The nominal size of the files in bytes. This is just an approximation. Defaults to ``None``, which means
            the search for corrupted files will not be performed.
        tolerance:
            Maximum allowed relative difference in file size, before it can be marked as corrupted.
            Any file whose size (``file_size``) satisfies ``abs(1 - file_size/nominal_size) > tolerance`` will be
            marked as corrupted. Defaults to ``0.01``, i.e. any file with a size difference larger than 1 percent of
            the nominal size will be marked as corrupted.
        number_of_processes:
            The number of process used to get the size of files concurrently. Defaults to ``20``. A value of ``1``
            disables multiprocessing. This is useful for testing purposes.

    Returns:
        A 2-tuple of sets, where the first and second sets include missing and corrupted files, respectively.
    """
    missing_files, corrupted_files = None, None

    if transform_function:
        files_transformed = {transform_function(f) for f in files}
    else:
        files_transformed = set(files)

    if reference_list:
        missing_files = set(reference_list) - files_transformed

    if nominal_size:
        if number_of_processes > 1:
            results = run_multiple_processes(os.path.getsize, files, number_of_processes=number_of_processes)
            corrupted_files = {f for f, r in zip(files, results, strict=False) if abs(1 - r / nominal_size) > tolerance}
        else:
            corrupted_files = {f for f in files if abs(1 - f.stat().st_size / nominal_size) > tolerance}

    return missing_files, corrupted_files
