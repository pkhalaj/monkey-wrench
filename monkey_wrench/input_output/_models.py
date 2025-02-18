import os
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Literal, TypeVar

from loguru import logger
from pydantic import FilePath, NonNegativeFloat, NonNegativeInt, validate_call

from monkey_wrench.generic import ListSetTuple, Model, Pattern, StringTransformation, TransformFunction
from monkey_wrench.input_output._types import (
    AbsolutePath,
    ExistingDirectoryPath,
    ExistingFilePath,
    NewFilePath,
    WriteMode,
)
from monkey_wrench.process import MultiProcess
from monkey_wrench.query import Batches

T = TypeVar("T")
R = TypeVar("R")


class ExistingInputFile(Model):
    input_filepath: ExistingFilePath


class InputFile(Model):
    input_filepath: ExistingFilePath | NewFilePath | None = None


class NewOutputFile(Model):
    output_filepath: NewFilePath


class OutputFile(Model):
    output_filepath: ExistingFilePath | NewFilePath | None = None


class ModelFile(Model):
    model_filepath: ExistingFilePath


class InputDirectory(Model):
    input_directory: ExistingDirectoryPath


class OutputDirectory(Model):
    output_directory: ExistingDirectoryPath


class ParentDirectory(Model):
    parent_directory: ExistingDirectoryPath
    """The top level directory where the child directories reside."""


class FsSpecCache(Model):
    fsspec_cache: Literal["filecache", "blockcache"] | None = None
    """How to buffer, e.g. ``"filecache"``, ``"blockcache"``, or ``None``. Defaults to ``None``.

    See `fsspec cache <fs>`_, to learn more about buffering and random access in `fsspec`.

    .. _fs: https://filesystem-spec.readthedocs.io/en/latest/features.html#file-buffering-and-random-access

    Warning:
        ``None`` might lead to too many requests being sent to the server!
    """

    @property
    def fsspec_cache_str(self):
        """Return the cache string with a leading ``::`` if it is not ``None``. Otherwise, return an empty string."""
        return f"::{self.fsspec_cache}" if self.fsspec_cache else ""


class DatasetSaveOptions(Model):
    dataset_save_options: dict[str, bool | str | int] = dict(
        writer="cf",
        include_lonlats=False
    )
    """Storage options using which the dataset is to be saved. This is dataset-dependent.

    The default behaviour is to use ``cf`` as the writer and exclude longitude and latitude values, i.e.
    ``dataset_save_options = dict(writer="cf", include_lonlats=False)``
    """


class Writer(OutputFile):
    """Pydantic model for an ASCII file writer."""

    write_mode: WriteMode = "w"
    """Defaults to ``"w"``."""

    pre_writing_transformation: StringTransformation = StringTransformation()
    """The transformation before writing items to the file.

    Defaults to :obj:`monkey_wrench.generic.StringTransformation()`, which means the items will be trimmed.

    Note:
        The items will be first transformed according to the ``pre_writing_transformation.transform_function``, and
        then trimmed.
    """

    on_write_raise_exceptions: list[type[Exception]] | None = None
    """A list of exceptions which will be caught and logged as warnings.

    Defaults to ``None``, which means all exceptions will be caught. If it is a tuple, only the given exceptions will be
    caught. As a result, in the case of an empty list, no exceptions will be caught.
    """

    def __get_write_mode(self, write_mode: WriteMode | None = None):
        """Return the ``write_mode`` if it is not ``None``. Otherwise return the value of ``self.write_mode``."""
        if write_mode is None:
            return self.write_mode
        return write_mode

    def prepare_file_for_writing(self, write_mode: WriteMode | None = None) -> None:
        """Prepare the file depending on whether the file exists and the value of ``write_mode``.

        Note:
            - If the file exists and ``write_mode`` is ``"a"``, the file will be left as it is.
            - If the file exists and ``write_mode`` is ``"w"``, the file will be overwritten.
            - If the file does not exist, the file will be created, regardless of ``write_mode``.

        Args:
            write_mode:
                Defaults to ``None``, which means the value from ``self.write_mode`` will be used.
        """
        with open(self.output_filepath, self.__get_write_mode(write_mode)):
            pass

    def write(
            self,
            items: ListSetTuple | Generator[Any, None, None],
            write_mode: WriteMode | None = None,
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

        with open(self.output_filepath, self.__get_write_mode(write_mode)) as f:
            for item in items:
                try:
                    item = self.pre_writing_transformation.transform_items(item)
                    item = self.pre_writing_transformation.trim_items(item)
                    f.write(item + "\n")
                    number_of_items += 1
                except Exception as exception:
                    if self.on_write_raise_exceptions is None:
                        continue
                    if isinstance(exception, tuple(*self.on_write_raise_exceptions)):
                        logger.warning(f"Failed attempt to write {item} to text file {self.path}: {exception}")
                    raise exception

        return number_of_items

    def write_in_batches(self, batches: Batches, write_mode: WriteMode | None = None) -> NonNegativeInt:
        """Similar to :func:`write`, but assumes that the input is in batches."""
        self.prepare_file_for_writing(self.__get_write_mode(write_mode))
        number_of_items = 0
        for batch, _ in batches:
            number_of_items += self.write(batch, write_mode="a")
        return number_of_items


class Reader(ExistingInputFile):
    """Pydantic model for an ASCII file reader."""

    post_reading_transformation: StringTransformation = StringTransformation()
    """The transformation after reading items from the file and before returning them.

    Defaults to :obj:`monkey_wrench.generic.StringTransformation()`, which means the items will be trimmed.

    Note:
        The items will be first trimmed and then trimmed according to
        ``post_reading_transformation.transform_function``.
    """

    def read(self) -> list[Any]:
        """Read items from a text file, assuming each line corresponds to a single item.

        Examples of items are product IDs.

        Warning:
            This function does not check whether the items are valid or not. It is a simple convenience function for
            reading items from a text file.

        Returns:
            A list of (transformed) items, where each item corresponds to a single line in the given file.
        """
        with open(self.input_filepath, "r") as f:
            items = f.readlines()

        items = self.post_reading_transformation.trim_items(items)
        items = self.post_reading_transformation.transform_items(items)

        return items


class DirectoryVisitor(ParentDirectory, Pattern):
    """Pydantic model for visiting a directory tree."""

    visitor_writer: Writer | None = None
    """If given, it will be used to dump the list of visited items to a file."""

    visitor_callback: TransformFunction[Path, Any] | None = None
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
            for root, _, files in os.walk(self.parent_directory):
                for file in files:
                    if self.pattern.exists_in(file):
                        files_list.append(Path(root, file))
        else:
            for item in os.listdir(self.parent_directory):
                if (file := Path(self.parent_directory, item)).is_file():
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

        if self.visitor_callback is not None:
            for f in files_list:
                self.visitor_callback(f)

        if self.visitor_writer is not None:
            self.visitor_writer.write(files_list)

        return files_list


class FilesIntegrityValidator(MultiProcess):
    """Pydantic model to verify the integrity of files by checking their size."""

    nominal_file_size: NonNegativeInt | None = None
    """The nominal size of files in bytes.

    Defaults to ``None``, which means the search for corrupted files will not be performed.
    """

    file_size_relative_tolerance: NonNegativeFloat = 0.01
    """The maximum relative difference in the size of a file, before it can be marked as corrupted.

    Defaults to ``0.01``, i.e. any file whose size differs by more than one percent from the nominal size, will be
    marked as corrupted.
    """

    filepath_transform_function: TransformFunction[Path, T] | None = None
    """A function to transform the file paths into other types of objects before comparing them against the reference.

    This can be e.g. a :func:`~monkey_wrench.date_time.DateTimeParser.parse` function to make datetime objects out of
    file paths. Defaults to ``None`` which means no transformation is performed and the given file paths and the
    reference items are compared as they are.
    """

    reference: ListSetTuple[T] | AbsolutePath[FilePath] | DirectoryVisitor | None = None
    """Reference items to compare against, used in finding the missing files.

    It can be a list/set/tuple of items, or a filepath from which the reference items can be read, or a directory
    visitor which can collect the reference items.

    Defaults to ``None`` which means the search for missing files will not be performed.
    """

    @staticmethod
    def get_reference_items(
            reference: ListSetTuple[T] | AbsolutePath[FilePath] | DirectoryVisitor | None = None
    ) -> Any:
        match reference:
            case None:
                return None
            case Path():
                return Reader(input_filepath=reference).read()
            case DirectoryVisitor():
                return reference.visit()
            case _:
                return reference

    def __get_reference_items(
            self, reference: ListSetTuple[T] | AbsolutePath[FilePath] | DirectoryVisitor | None = None
    ) -> Any:
        if reference is None:
            reference = self.reference
        return FilesIntegrityValidator.get_reference_items(reference)

    def file_is_corrupted(self, file_size: NonNegativeInt) -> bool:
        return abs(1 - file_size / self.nominal_file_size) > self.file_size_relative_tolerance

    @validate_call
    def find_corrupted_files(self, filepaths: ListSetTuple[Path]) -> set[Path] | None:
        if self.nominal_file_size is None:
            return None

        file_sizes = self.run_with_results(os.path.getsize, filepaths)
        return {fp for fp, fs in zip(filepaths, file_sizes, strict=True) if self.file_is_corrupted(fs)}

    @validate_call
    def transform_files(self, filepaths: ListSetTuple[Path]) -> set[Path]:
        return {self.filepath_transform_function(f) for f in filepaths} if self.filepath_transform_function else set(
            filepaths)

    @validate_call
    def find_missing_files(
            self,
            filepaths: ListSetTuple[Path],
            reference: ListSetTuple[T] | AbsolutePath[FilePath] | DirectoryVisitor | None = None
    ) -> set[Path] | None:
        reference = self.__get_reference_items(reference)
        return (set(reference) - self.transform_files(filepaths)) if reference else None

    @validate_call
    def verify_files(
            self,
            filepaths: ListSetTuple[Path],
            reference: ListSetTuple[T] | AbsolutePath[FilePath] | DirectoryVisitor | None = None
    ) -> tuple[set[T] | None, set[Path] | None]:
        """Check for missing and corrupted files."""
        return self.find_missing_files(filepaths, reference), self.find_corrupted_files(filepaths)


class DateTimeDirectory(ParentDirectory):
    datetime_format_string: str = "%Y/%m/%d"
    """The format string to create subdirectories from the datetime object. Defaults to ``"%Y/%m/%d"``."""

    reset_child_datetime_directory: bool = False
    """A boolean to determine whether to remove the (child) directory first if it already exists. Defaults to ``False``.

    This might save us from some issues regrading files being overwritten and corrupted.
    """

    def get_datetime_directory(self, datetime_object: datetime) -> Path:
        """Get the full path to the datetime directory (given the datetime object). This does not create the directory.

        Args:
            datetime_object:
                The datetime object for which the full directory path will be returned.

        Returns:
            The full path of the datetime directory.

        Example:
            >>> path = DateTimeDirectory(
            ...  datetime_format_string="%Y/%m/%d",
            ...  parent_directory=Path.home()
            ... ).get_datetime_directory(
            ...  datetime(2022, 3, 12)
            ... )
            >>> expected_path = Path.home() / Path("2022/03/12")
            >>> expected_path == path
            True
        """
        dir_path = self.parent_directory / Path(datetime_object.strftime(self.datetime_format_string))
        return dir_path

    def create_datetime_directory(self, datetime_object: datetime) -> Path:
        """Create a directory based on the datetime object.

        Args:
            datetime_object:
                The datetime object to create the directory for.

        Returns:
            The full path of the (created) directory.

        Example:
            >>> path = DateTimeDirectory(
            ...  datetime_format_string="%Y/%m/%d",
            ...  parent_directory=Path.home()
            ... ).create_datetime_directory(
            ...  datetime(2022, 3, 12)
            ... )
            >>> expected_path = Path.home() / Path("2022/03/12")
            >>> expected_path.exists()
            True
            >>> expected_path == path
            True
        """
        dir_path = self.get_datetime_directory(datetime_object)
        if dir_path.exists() and self.reset_child_datetime_directory:
            dir_path.unlink()
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
