"""The module which includes common functions used in testing."""

import os
import random
import sys
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable
from unittest.mock import MagicMock, patch

import numpy as np
import yaml
from pydantic import NonNegativeInt, validate_call

from monkey_wrench.date_time import DateTimePeriod
from monkey_wrench.input_output import DateTimeDirectory, seviri

DateTimeLike = Iterable[int]
"""Type definition for a datetime like object such as ``[2022, 10, 27]``."""


def noop(*_args, **_kwargs):
    """Dummy function."""
    pass


class EnvironmentVariables:
    """A context manager to manipulate environment variables and restoring them upon exit."""

    def __init__(self, **kwargs: dict[str, Any]):
        """Initialise the context manager by making a copy of the original environment variables.

        Args:
            **kwargs:
                Environment variables that are to be manipulated within the context manager.

        Note:
            Any (new) variable with a value of ``None`` will be ignored, unless it exists in the original environment.
            In this case, the variable will be deleted from the new environment.
        """
        self.__kwargs = {k: v for k, v in kwargs.items()}
        self.__original_env = {k: v for k, v in os.environ.items()}

    def __enter__(self):
        """Enter the context manager by performing the actual manipulation of the environment variables."""
        for k, v in self.__kwargs.items():
            if v:
                os.environ[k] = str(v)
            if v is None and k in self.__original_env.keys():
                del os.environ[k]

    def __delete_newly_added_variables(self):
        """Delete all environment variables that did not exist in the original environment."""
        for k in os.environ.keys():
            if k not in self.__original_env.keys():
                del os.environ[k]

    def __reset_variables_to_original_values(self):
        """Reset all environment variables to their original values."""
        for k, v in self.__original_env.items():
            os.environ[k] = v

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore the original environment."""
        self.__delete_newly_added_variables()
        self.__reset_variables_to_original_values()


@contextmanager
def cli_arguments(*args, starting_index: int = 1):
    """A context manager to manipulate CLI arguments and restoring them upon exit.

    Args:
        *args:
            CLI arguments, as a list, that needs to be replaced.
        starting_index:
            The index of the CLI argument to start with. Defaults to ``1``, meaning the path of the executable will
            not be changed.
    """
    _original_args = deepcopy(sys.argv)
    try:
        sys.argv[starting_index:] = deepcopy(args)
        yield
    finally:
        sys.argv = deepcopy(_original_args)


def shuffle_list(lst: list[Any]) -> tuple[list[int], list[Any]]:
    """Shuffle the given list.

    Args:
        lst: List to be shuffled.

    Returns:
        A 2-tuple in which the first element is the list of shuffled indices, and the second element is the shuffled
        list.
    """
    indexed_list = list(enumerate(lst))
    random.shuffle(indexed_list)

    shuffled_indices = [i for i, _ in indexed_list]
    shuffled_lst = [v for _, v in indexed_list]

    return shuffled_indices, shuffled_lst,


def get_items_from_shuffled_list_by_original_indices(
        tuple_of_shuffled_indices_list: tuple[list[int], list[Any]], original_indices: list
) -> list[Any]:
    """Get items from a shuffled list given the shuffled indices and original indices.

    Args:
        tuple_of_shuffled_indices_list:
            This is basically the return value of :func:`shuffle_list`.
        original_indices:
            Original indices of items in the original list.

    Returns:
        The list of retrieved items from the original index.
    """
    shuffled_indices, shuffled_lst = tuple_of_shuffled_indices_list
    return [shuffled_lst[shuffled_indices.index(index)] for index in shuffled_indices if index in original_indices]


def convert_datetime_like_items_to_datetime_objects(datetime_like_items: Iterable[DateTimeLike]) -> Iterable[datetime]:
    """Convert an iterable of datetime like items into an iterable of datetime objects."""
    return (datetime(*p) for p in datetime_like_items)


def intervals_equal(
        expected_interval: timedelta,
        lst: Iterable[tuple[datetime, datetime]] | Iterable[datetime] | Iterable[DateTimePeriod]
) -> bool:
    """Check if all items in the list have the same interval.

    In case of an iterable of 2-tuples, the interval is calculated by subtracting the second element of the tuple from
    the first one.

    Args:
        expected_interval:
            The expected interval.
        lst:
            Either an iterable of 2-tuples of datetime objects, or an iterable of single datetime objects.

    Raises:
        ValueError:
            If the ``lst`` is not either an iterable of 2-tuples or an iterable of single datetime objects.
    """
    if all(isinstance(i, datetime) for i in lst):
        return all([expected_interval == lst[i + 1] - lst[i] for i in range(len(lst) - 1)])

    if all([isinstance(t, tuple) and len(t) == 2 for t in lst]):
        return all([expected_interval == i - j] for i, j in lst)

    if all([isinstance(t, DateTimePeriod) for t in lst]):
        return all([expected_interval == dt.end_datetime - dt.start_datetime] for dt in lst)

    raise ValueError("All items in the list must be either single or 2-tuples of datetime objects.")


def make_dummy_file(filename: Path, size_in_bytes: int = 1) -> Path:
    """Make a dummy file filled with zero bytes with the given size.

    Args:
        filename:
            Path to the file to be created.
        size_in_bytes:
            The size of the file to be created in bytes. Defaults to ``1``.

    Returns:
        Path to the created dummy file.
    """
    with open(filename, "wb") as f:
        f.write(b"\0" * size_in_bytes)
    return filename


@validate_call
def randomly_remove_from_list(
        items: list,
        number_of_items_to_remove: NonNegativeInt,
        callback: Callable | None = None,
) -> tuple[set, set, set]:
    """Randomly remove items from a list.

    The ``callback`` is a function that will be called once for each item that is removed from the list. Each removed
    item is passed to the ``callback`` as an argument.

    Returns:
        A 3-tuple in which the elements are, set of all items (shuffled), list of available items, and
        set of removed items.
    """
    if number_of_items_to_remove > len(items):
        raise ValueError("Number of items to remove must be less than the number of items in the list.")

    _, shuffled_items = shuffle_list(items)
    available_items = {i for i in shuffled_items}
    removed_items = set()

    if number_of_items_to_remove > 0:
        _n = -1 * number_of_items_to_remove
        removed_items = set(shuffled_items[_n:])

    if callback:
        for item in removed_items:
            callback(item)

    available_items -= removed_items

    return set(shuffled_items), available_items, removed_items


@validate_call
def make_dummy_files(
        directory: Path,
        filenames: Iterable[Path] = None,
        prefix: str = "",
        extension: str = ".dummy",
        number: int = 3,
        nominal_size_in_bytes: int = 1000,
        tolerance: float = 0.01,
        size_fluctuation_ratio: float | None = None,
        number_of_files_to_remove: int = 0,
) -> tuple[set[Path], set[Path], set[Path]]:
    """Make a number of dummy files.

    Args:
        directory:
            The directory inside which the files will be created.
        filenames:
            The filenames for the files to be created. Defaults to ``None``, which means the filenames will be
            enumerated from ``0`` to ``number-1``. If this is given, the ``number``, ``prefix``, and ``extension``
            will be all ignored.
        prefix:
            The beginning of filenames. Defaults to ``""``.
        extension:
            The file extension. Defaults to ``".dummy"``.
        number:
            The number of files to create. Defaults to ``3``.
        nominal_size_in_bytes:
            The nominal or expected size of files in bytes. Defaults to ``1000``. The actual size of each file will be
            a random value drawn from a normal distribution with an average value of ``nominal_size_in_bytes`` and a
            standard deviation of ``size_fluctuation_ratio x nominal_size_in_bytes``. This is to simulate the effect of
            file corruption, i.e. when the difference in expected file size and actual file size is beyond some given
            tolerance.
        tolerance:
            Maximum allowed relative difference in file size, before it can be marked as corrupted.
            Any file whose size (``file_size``) satisfies ``abs(1 - file_size/nominal_size) > tolerance`` will be
            marked as corrupted. Defaults to ``0.01``, i.e. any file with a size difference larger than 1 percent of
            the expected size will be marked as corrupted.
        size_fluctuation_ratio:
            See the description of ``nominal_size_in_bytes`` and ``tolerance``. Defaults to ``None``, which means all
            files will have the same size of ``nominal_size_in_bytes``.
        number_of_files_to_remove:
            The number of files to remove randomly. Defaults to ``0``. This is to simulate the effect of missing files.

    Returns:
        A 3-tuple in which the elements are list of all files, set of removed (missing) files, set of corrupted files.
    """
    files = []

    def _create_file(fname):
        files.append(directory / fname)
        make_dummy_file(
            files[-1],
            size_in_bytes=nominal_size_in_bytes if size_fluctuation_ratio is None else int(
                np.random.normal(nominal_size_in_bytes, size_fluctuation_ratio * nominal_size_in_bytes))
        )

    if filenames is None:
        for i in range(number):
            _create_file(directory / Path(f"{prefix}{i}{extension}"))
    else:
        for filename in filenames:
            _create_file(directory / filename)

    shuffled_files, available_files, missing_files = randomly_remove_from_list(
        files, number_of_files_to_remove, callback=os.remove
    )

    if size_fluctuation_ratio is not None:
        corrupted_files = {
            f for f in available_files if abs(1 - f.stat().st_size / nominal_size_in_bytes) > tolerance
        }
    else:
        corrupted_files = set()

    return shuffled_files, missing_files, corrupted_files


def make_yaml_file(filename: Path, yaml_context_as_dict: dict) -> Path:
    """Make a yaml file out of the given dictionary."""
    with open(filename, "w") as f:
        yaml.dump(yaml_context_as_dict, f, default_flow_style=False)
    return filename


@contextmanager
def optional_modules_mocked():
    """Context manager to mock modules such as CHIMP."""
    modules_tree = {k: MagicMock() for k in ["chimp", "chimp.areas", "chimp.processing"]}
    with patch.dict(sys.modules, modules_tree) as _module:
        chimp = _module["chimp"]
        chimp.areas = _module["chimp.areas"]
        chimp.processing = _module["chimp.processing"]

        chimp.processing.cli = MagicMock(name="chimp.processing.cli")
        yield chimp


def make_dummy_datetime_files(datetime_objs: list[datetime], parent: Path) -> list[Path]:
    files = []
    for datetime_obj in datetime_objs:
        dir_path = DateTimeDirectory(parent_directory=parent).create(datetime_obj)
        filename = seviri.input_filename_from_datetime(datetime_obj)
        files.append(make_dummy_file(dir_path / filename))
    return files
