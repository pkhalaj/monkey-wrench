import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Generator, Literal, TypeVar

from loguru import logger
from pydantic import DirectoryPath, FilePath, NewPath, NonNegativeFloat, NonNegativeInt, field_validator, validate_call

from monkey_wrench.generic import Function, ListSetTuple, Model, Pattern
from monkey_wrench.input_output._types import AbsolutePath
from monkey_wrench.process import MultiProcess
from monkey_wrench.query import Batches

T = TypeVar("T")
R = TypeVar("R")


class ExistingInputFile(Model):
    input_filepath: AbsolutePath[FilePath]


class InputFile(Model):
    input_filepath: AbsolutePath[FilePath] | AbsolutePath[NewPath] | None = None


class NewOutputFile(Model):
    output_filepath: AbsolutePath[NewPath]


class OutputFile(Model):
    output_filepath: AbsolutePath[NewPath] | AbsolutePath[FilePath] | None = None


class ModelFile(Model):
    model_filepath: AbsolutePath[FilePath]


class InputDirectory(Model):
    input_directory: AbsolutePath[DirectoryPath]


class OutputDirectory(Model):
    output_directory: AbsolutePath[DirectoryPath]


class TempDirectory(Model):
    """Pydantic for a temporary directory."""
    temp_directory: AbsolutePath[DirectoryPath]

    @contextmanager
    def __call__(self) -> Generator[Path, None, None]:
        """Create a temporary directory and set the global temporary directory to the given path.

        Note:
            The reason to set the global temporary directory is to ensure that any other inner functions or context
            managers that might invoke ``tempfile.TemporaryDirectory()`` also use the given global temporary directory.

        Yields:
            The full path of the (created) temporary directory.
        """
        _default_tempdir = tempfile.gettempdir()
        try:
            with tempfile.TemporaryDirectory(dir=self.temp_directory) as _dir:
                tempfile.tempdir = _dir
                yield Path(_dir)
        finally:
            tempfile.tempdir = _default_tempdir


class FsSpecCache(Model):
    cache: Literal["filecache", "blockcache"] | None = None
    """How to buffer, e.g. ``"filecache"``, ``"blockcache"``, or ``None``. Defaults to ``None``.

    See `fsspec cache <fs>`_, to learn more about buffering and random access in `fsspec`.

    .. _fs: https://filesystem-spec.readthedocs.io/en/latest/features.html#file-buffering-and-random-access
    """

    @property
    def cache_str(self):
        return f"::{self.cache}" if self.cache else ""


class DatasetSaveOptions(Model):
    dataset_save_options: dict[str, bool | str | int] = dict(writer="cf", include_lonlats=False)
    """Storage options using which the dataset is to be saved.

    The default behaviour is to use ``cf`` as the writer and exclude longitude and latitude values, i.e.
    ``save_datasets_options = dict(writer="cf", include_lonlats=False)``
    """


class FileIO(Model):
    transform_function: Function[T, R] | Callable[[T], Any] | None = None
    """If given, each item in the list will be first transformed according to the function, before writing or reading.

    Defaults to ``None``, which means no transformation is performed and items will be treated as they are.
    """

    trim: bool = True
    """A boolean indicating whether to remove trailing/leading whitespaces, tabs, and newlines from each item.

    Defaults to ``True``.
    """


class Writer(FileIO, OutputFile):
    write_mode: Literal["w", "a"] = "w"
    """Either ``"a"`` for appending to, or ``"w"`` for overwriting an existing file. Defaults to ``"w"``."""

    exceptions: list[type[Exception]] | None = None
    """A list of exceptions which will be caught and logged as warnings.

    Defaults to ``None``, which means all exceptions will be caught. If it is a tuple, only the given exceptions will be
    caught. As a result, in the case of an empty list, no exceptions will be caught.
    """

    def create_output_file(self):
        """Create the output file."""
        with open(self.output_filepath, self.write_mode):
            pass

    def write(
            self,
            items: ListSetTuple | Generator[Any, None, None],
            write_mode: str | None = None,
    ) -> NonNegativeInt:
        """Write items from an iterable (list, set, tuple, generator) to a text file, with one item per line.

        Examples of items are product IDs.

        This function opens a text file in the `write` or `append` mode. It then writes each item from the provided
        iterable to the file. It catches any potential errors during the writing process, and logs a warning.

        Args:
            items:
                An iterable of items to be written to the file.
            write_mode:
                Defaults to ``None``, which means the value from ``self.write_mode`` will be used.

        Returns:
            The number of items that are written to the file successfully.
        """
        number_of_items = 0

        with open(self.output_filepath, write_mode or self.write_mode) as f:
            for item in items:
                try:
                    item = self.transform_function(item) if self.transform_function is not None else item
                    item_str = str(item)
                    item_str = (item_str.strip() if self.trim else item_str) + "\n"
                    f.write(item_str)
                    number_of_items += 1
                except Exception as exception:
                    if self.exceptions is None:
                        continue
                    if isinstance(exception, tuple(*self.exceptions)):
                        logger.warning(f"Failed attempt to write {item} to text file {self.path}: {exception}")
                    raise exception

        return number_of_items

    def write_in_batches(self, batches: Batches) -> NonNegativeInt:
        """Similar to :func:`write`, but assumes that the input is in batches."""
        self.create_output_file()
        number_of_items = 0
        for batch, _ in batches:
            number_of_items += self.write(batch, write_mode="a")
        return number_of_items


class Reader(FileIO, InputFile):
    def read(self) -> list[Any]:
        """Get the list of items from a text file, assuming each line corresponds to a single item.

        Examples of items are product IDs.

        Warning:
            This function does not check whether the items are valid or not. It is a simple convenience function for
            reading items from a text file.

        Returns:
            A list of (transformed) items, where each item corresponds to a single line in the given file.
        """
        with open(self.input_filepath, "r") as f:
            items = f.readlines()

        if self.trim:
            items = [item.strip() for item in items]

        if self.transform_function:
            return [self.transform_function(i) for i in items]

        return items


class DirectoryVisitor(InputDirectory, Writer, Pattern):
    """Pydantic model for visiting a directory tree."""

    @property
    def pattern(self):
        return Pattern(sub_strings=self.sub_strings, case_sensitive=self.case_sensitive, match_all=self.match_all)

    callback: Function[Path, Any] | Callable[[Path], Any] | None = None
    """A function that will be called everytime a match is found for a file. Defaults to ``None``."""

    reverse: bool = False
    """A boolean to determine whether to sort the files in reverse order.

    Defaults to ``False``, which means sorting is in the alphabetical order.
    """

    recursive: bool = True
    """Determines whether to recursively visit the directory tree. or just visit the top-level directory.

    Defaults to ``True``.
    """

    def __collect_files(self) -> list[Path]:
        files_list = []

        if self.recursive:
            for root, _, files in os.walk(self.input_directory):
                for file in files:
                    if self.pattern.exists_in(file):
                        files_list.append(Path(root, file))
        else:
            for item in os.listdir(self.input_directory):
                if (file := Path(self.input_directory, item)).is_file():
                    if self.pattern.exists_in(item):
                        files_list.append(file)

        return sorted(files_list, reverse=self.reverse)

    def visit(self):
        """Visit all files in the directory, either recursively or just the top-level files.

        Returns:
            A sorted flat list of all file paths in the given directory that match the given pattern and have been
            treated according to the ``callback`` function.
        """
        files_list = self.__collect_files()

        if self.callback is not None:
            for f in files_list:
                self.callback(f)

        if self.output_filepath is not None:
            self.write(files_list)

        return files_list


class FilesIntegrityValidator(MultiProcess):
    """Pydantic model to verify the integrity of files by checking their size."""

    nominal_size: NonNegativeInt | None = None
    """The nominal size of files in bytes.

    Defaults to ``None``, which means the search for corrupted files will not be performed.
    """

    tolerance: NonNegativeFloat = 0.01
    """The maximum relative difference in the size of a file, before it can be marked as corrupted.

    Defaults to ``0.01``, i.e. any file whose size differs by more than one percent from the nominal size, will be
    marked as corrupted.
    """

    transform_function: Function[Path, T] | Callable[[Path], T] | None = None
    """A function to transform the files into new objects before comparing them against the reference.

    This can be e.g. a :func:`~monkey_wrench.date_time.DateTimeParser.parse` function to make datetime objects out of
    file paths. Defaults to ``None`` which means no transformation is performed and the given file paths and the
    reference items are compared as they are.
    """

    reference: ListSetTuple[T] | AbsolutePath[FilePath] | DirectoryVisitor | None = None
    """Reference items to compare against for finding the missing files.

    Defaults to ``None`` which means the search for missing files will not be performed.
    """

    @field_validator("reference", mode="after")
    def validate_reference_items_from_file(cls, reference: Any) -> Any:
        if isinstance(reference, Path):
            return Reader(input_filepath=reference).read()
        if isinstance(reference, DirectoryVisitor):
            return reference.visit()
        return reference

    def is_corrupted(self, file_size: NonNegativeInt) -> bool:
        return abs(1 - file_size / self.nominal_size) > self.tolerance

    @validate_call
    def find_corrupted_files(self, filepaths: ListSetTuple[Path]) -> set[Path] | None:
        if self.nominal_size is None:
            return None

        file_sizes = self.run(os.path.getsize, filepaths)
        return {fp for fp, fs in zip(filepaths, file_sizes, strict=True) if self.is_corrupted(fs)}

    @validate_call
    def transform_files(self, filepaths: ListSetTuple[Path]) -> set[Path]:
        return {self.transform_function(f) for f in filepaths} if self.transform_function else set(filepaths)

    @validate_call
    def find_missing_files(self, filepaths: ListSetTuple[Path]) -> set[Path] | None:
        return set(self.reference) - self.transform_files(filepaths) if self.reference else None

    @validate_call
    def verify(self, filepaths: ListSetTuple[Path]) -> tuple[set[T] | None, set[Path] | None]:
        return self.find_missing_files(filepaths), self.find_corrupted_files(filepaths)
