"""The module providing functions to handle IO operations and manipulations of files and filenames."""

import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Generator

import requests
from loguru import logger
from pydantic import DirectoryPath, FilePath, NewPath, NonNegativeInt, PositiveInt, validate_call

from monkey_wrench.generic import ListSetTuple, Order, StringOrStrings, pattern_exists
from monkey_wrench.input_output._types import AbsolutePath, WriteMode
from monkey_wrench.process import run_multiple_processes
from monkey_wrench.query import Batches


@validate_call
def visit_files_in_directory(
        directory: AbsolutePath[DirectoryPath],
        callback: Callable | None = None,
        pattern: StringOrStrings | None = None,
        order: Order = Order.ascending,
        recursive: bool = True,
        **kwargs
) -> list[Path]:
    """Visit all files in the directory, either recursively or just the top-level files.

    Note:
        This function relies on :func:`~monkey_wrench.generic.pattern_exists`.

    Args:
        directory:
            The top-level directory to collect the files from.
        callback:
            A function that will be called everytime a match is found for a file. Defaults to ``None``.
        pattern:
            If given, it will be used to filter files, i.e. a file must have the pattern item(s) as (a) substring(s) in
            its name. Defaults to ``None`` which means no filtering. See :func:`~monkey_wrench.generic.pattern_exists`
            for more information.
        order:
            Either :obj:`~monkey_wrench.date_time.Order.descending` or :obj:`~monkey_wrench.date_time.Order.ascending`.
            Defaults to :obj:`~monkey_wrench.date_time.Order.ascending`.
        recursive:
            A boolean flag determining whether to recursively visit all files in the directory tree, or just visit files
            in the top-level directory. Defaults to ``True``.
        kwargs:
            Other keyword arguments that will be directly passed to :func:`~monkey_wrench.generic.pattern_exists`.

    Returns:
        A sorted flat list of all file paths in the given directory that match the given pattern and have been treated
        according to the ``callback`` function.
    """
    file_list = []

    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if pattern_exists(file, pattern, **kwargs):
                    file_list.append(Path(root, file))
    else:
        for item in os.listdir(directory):
            if (file := Path(directory, item)).is_file():
                if pattern_exists(item, pattern, **kwargs):
                    file_list.append(file)

    if callback is not None:
        for f in file_list:
            callback(f)

    return sorted(file_list, reverse=(order == Order.descending))


@validate_call
def copy_files_between_directories(
        source_directory: AbsolutePath[DirectoryPath],
        destination_directory: AbsolutePath[DirectoryPath],
        pattern: StringOrStrings = None,
        **kwargs
) -> None:
    """Copy (top-level) files whose filename match the pattern from one directory to another.

    Warning:
        The copying is not performed recursively. Only the top-level files are copied.

    Note:
        This function relies on :func:`~monkey_wrench.generic.pattern_exists`.

    Args:
        source_directory:
            The source directory to copy files from.
        destination_directory:
            The destination directory to copy files to.
        pattern:
            The pattern to filter the files.
        kwargs:
            Other keyword arguments that will be directly passed to :func:`~monkey_wrench.generic.pattern_exists`.
    """
    visit_files_in_directory(
        source_directory,
        lambda f: copy_single_file_to_directory(destination_directory, f),
        pattern=pattern,
        recursive=False,
        **kwargs
    )


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
def write_items_to_txt_file(
        items: ListSetTuple | Generator,
        items_list_filepath: AbsolutePath[FilePath] | AbsolutePath[NewPath],
        write_mode: WriteMode = WriteMode.overwrite
) -> NonNegativeInt:
    """Write items from an iterable (list, set, tuple, generator) to a text file, with one item per line.

    Examples of items are product IDs.

    This function opens a text file in write or append mode and writes each item from the provided iterable to the file.
    It catches any potential errors during the writing process, and logs a warning.

    Args:
        items:
            An iterable of items to be written to the file.
        items_list_filepath:
            The path to the (text) file where the items will be written.
        write_mode:
            Either :obj:`~monkey_wrench.input_output.WriteMode.append` or
            :obj:`~monkey_wrench.input_output.WriteMode.overwrite`.
            Defaults to :obj:`~monkey_wrench.input_output.WriteMode.overwrite`.

    Returns:
        The number of items that are written to the file successfully.
    """
    number_of_items = 0
    with open(items_list_filepath, write_mode.value) as f:
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
        batches: Batches, items_list_filepath: AbsolutePath[FilePath] | AbsolutePath[NewPath]
) -> NonNegativeInt:
    """Similar to :func:`write_items_to_txt_file`, but assumes that the input is in batches."""
    # First, create an empty file.
    with open(items_list_filepath, "w"): ...

    number_of_items = 0
    for batch, _ in batches:
        number_of_items += write_items_to_txt_file(batch, items_list_filepath, write_mode=WriteMode.append)
    return number_of_items


@validate_call
def read_items_from_txt_file(
        items_list_filepath: AbsolutePath[FilePath],
        transform_function: Callable | None = None,
        trim: bool = True,
) -> list[Any]:
    """Get the list of items from a text file, assuming each line corresponds to a single item.

    Examples of items are product IDs.

    Warning:
        This function does not check whether the items are valid or not. It is a simple convenience function for reading
        items from a text file.

    Args:
        items_list_filepath:
            The path to the (text) file containing the list of items.
        transform_function:
            If given, each item in the list will be first transformed according to the function before being
            appended to the list and returned. Defaults to ``None``, which means no transformation is performed and
            items will be returned as they are.
        trim:
            A boolean indicating whether to remove trailing/leading whitespaces, tabs, and newlines from each item.
            Defaults to ``True``.

    Returns:
        A list of (transformed) items, where each item corresponds to a single line in the given file.
    """
    with open(items_list_filepath, "r") as f:
        items = f.readlines()

    if trim:
        items = [item.strip() for item in items]

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
        >>> from datetime import datetime
        >>> from pathlib import Path
        >>> from monkey_wrench.input_output import create_datetime_directory
        >>>
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


@contextmanager
@validate_call
def temp_directory(directory: AbsolutePath[DirectoryPath]) -> Path:
    """Create a temporary directory and set the global temporary directory to the given path.

    Note:
        The reason to set the global temporary directory is to ensure that any other inner functions or context managers
         that might invoke ``tempfile.TemporaryDirectory()`` also use the given global temporary directory.

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
        filepaths: ListSetTuple[Path],
        reference_items: ListSetTuple | None = None,
        transform_function: Callable | None = None,
        nominal_size: int | None = None,
        tolerance: float = 0.01,
        number_of_processes: PositiveInt = 20,
) -> tuple[set | None, set | None]:
    """Compare an iterable of file paths with an iterable of reference items and report missing and corrupted files.

    Warning:
        This function will convert iterables into sets. As a result, duplicate items are removed.

    Args:
        filepaths:
            The iterable of file paths to perform the check on.
        reference_items:
            The reference iterable of items to compare against. Defaults to ``None`` which means the search for
            missing files will not be performed.
        transform_function:
            A function to transform the files into new objects before comparing them against the reference. This can be
            e.g. a :func:`~monkey_wrench.date_time.DateTimeParser.parse` function to make datetime objects out of
            file paths. Defaults to ``None`` which means no transformation is performed and the given file paths and the
            reference items are compared as they are.
        nominal_size:
            The nominal size of the files in bytes. Defaults to ``None``, which means the search for corrupted files
            will not be performed.
        tolerance:
            The maximum relative difference in file size, before it can be marked as corrupted.
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
        files_transformed = {transform_function(f) for f in filepaths}
    else:
        files_transformed = set(filepaths)

    if reference_items:
        missing_files = set(reference_items) - files_transformed

    if nominal_size:
        if number_of_processes > 1:
            results = run_multiple_processes(os.path.getsize, filepaths, number_of_processes=number_of_processes)
            corrupted_files = {f for f, r in zip(filepaths, results, strict=True) if
                               abs(1 - r / nominal_size) > tolerance}
        else:
            corrupted_files = {f for f in filepaths if abs(1 - f.stat().st_size / nominal_size) > tolerance}

    return missing_files, corrupted_files
