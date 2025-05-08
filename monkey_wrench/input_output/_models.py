import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Literal, TypeVar

from loguru import logger
from pydantic import AfterValidator, NonNegativeFloat, NonNegativeInt, validate_call
from typing_extensions import Annotated

from monkey_wrench.generic import ListSetTuple, Model, Pattern, StringTransformation, TransformFunction
from monkey_wrench.input_output._types import (
    ExistingDirectoryPath,
    ExistingFilePath,
    NewFilePath,
    OpenMode,
)
from monkey_wrench.process import MultiProcess
from monkey_wrench.query import Batches

ElementType = TypeVar("ElementType")
InputType = TypeVar("InputType")
ReturnType = TypeVar("ReturnType")
OtherReturnType = TypeVar("OtherReturnType")


class ExistingInputFile(Model):
    """Pydantic model for an input file which must exist.

    Example:
        A text file which includes the list of product IDs which have been already fetched. This file will be used to
        fetch the product files.
    """
    input_filepath: ExistingFilePath


class InputFile(Model):
    """Pydantic model for an input file which does not necessarily exist during the model validation."""
    input_filepath: ExistingFilePath | NewFilePath | None = None


class NewOutputFile(Model):
    """Pydantic mode for an output file which must not already exist.

    Example:
        A text file to store the result of visiting a directory, i.e. collected files that match the determined pattern.
    """
    output_filepath: NewFilePath


class OutputFile(Model):
    """Pydantic model for an output file which does not necessarily exist during the model validation."""
    output_filepath: ExistingFilePath | NewFilePath | None = None


class ModelFile(Model):
    """Pydantic model for a model file which must exist.

    Example:
        A ``*.pt`` file used by CHIMP, as the model, to perform a retrieval.
    """
    model_filepath: ExistingFilePath


class ParentInputDirectory(Model):
    """Pydantic model for the top-level directory where the child (input) directories reside. The directory must exist.

    Example:
        A directory which includes all SEVIRI files that have to be reprocessed using CHIMP.
    """
    parent_input_directory_path: ExistingDirectoryPath


class ParentOutputDirectory(Model):
    """Pydantic model for the top-level directory where the child (output) directories reside. The directory must exist.

    Example:
        A directory which the output of CHIMP will be saved.
    """
    parent_output_directory_path: ExistingDirectoryPath


class ExistingInputDirectory(Model):
    """Pydantic model for an input directory which must exist.

    Note:
        This model is to be solely used for a flat structure. If you have a hierarchical tree structure, use
        :obj:`~monkey_wrench.input_output._models.ParentInputDirectory` instead to be more clear about the directory
        structure.
    """
    input_directory: ExistingDirectoryPath


class ExistingOutputDirectory(Model):
    """Pydantic model for an output directory which must exist.

    Note:
        This model is to be solely used for a flat structure. If you have a hierarchical tree structure, use
        :obj:`~monkey_wrench.input_output._models.ParentOutputDirectory` instead to be more clear about the directory
        structure.
    """
    output_directory: ExistingDirectoryPath


class FsSpecCache(Model):
    """Pydantic model for the caching scheme of fsspec.

    Note:
        See `fsspec cache`_, to learn more about buffering and random access in `fsspec`.

    .. _fsspec cache: https://filesystem-spec.readthedocs.io/en/latest/features.html#file-buffering-and-random-access
    """

    fsspec_cache: Literal["filecache", "blockcache"] | None = None
    """How to buffer, e.g. ``"filecache"``, ``"blockcache"``, or ``None``. Defaults to ``None``.

    Warning:
        ``None`` might cause too many requests to be sent to the server!
    """

    @property
    def fsspec_cache_str(self):
        """Return the cache string with a leading ``::`` if it is not ``None``. Otherwise, return an empty string."""
        return f"::{self.fsspec_cache}" if self.fsspec_cache else ""


class DatasetSaveOptions(Model):
    """Pydantic model for the storage options using which the dataset is to be saved. This is dataset-dependent."""

    dataset_save_options: dict[str, bool | str | int] = dict(
        writer="cf",
        include_lonlats=False
    )
    """A dictionary which includes the actual storage options.

    The default behaviour is to use ``cf`` as the writer and exclude longitude and latitude values, i.e.
    ``dataset_save_options = dict(writer="cf", include_lonlats=False)``
    """


class Writer(OutputFile):
    """Pydantic model for an ASCII file (text mode) writer."""

    open_mode: OpenMode = "w"
    """The mode using which the text file will be opened. Defaults to ``"w"``."""

    pre_writing_transformation: StringTransformation = StringTransformation()
    """The transformation before writing items to the file.

    Defaults to `StringTransformation`_, which means the items will be only trimmed.

    Note:
        The items will first be transformed according to the ``pre_writing_transformation.transform_function``, and
        then trimmed.

    .. _StringTransformation: monkey_wrench.generic.StringTransformation
    """

    on_write_catch_exceptions: tuple[type[Exception], ...] | None = None
    """Exceptions which will be caught and logged as warnings.

    Defaults to ``None``, which means all exceptions will be caught. If it is a tuple, only the given exceptions will be
    caught. As a result, in the case of an empty tuple, no exceptions will be caught.
    """

    def __get_open_mode(self, open_mode: OpenMode | None = None):
        """Return the ``open_mode`` if it is not ``None``. Otherwise return the value of ``self.open_mode``."""
        if open_mode is None:
            return self.open_mode
        return open_mode

    def prepare_output_file_for_writing(self, open_mode: OpenMode | None = None) -> None:
        """Prepare the output file depending on whether the file exists and the value of ``open_mode``.

        Note:
            - If the file exists and ``open_mode`` is ``"a"``, the file will be left as it is.
            - If the file exists and ``open_mode`` is ``"w"``, the file will be overwritten.
            - If the file does not exist, the file will be created, regardless of ``open_mode``.

        Args:
            open_mode:
                Defaults to ``None``, which means the value from ``self.open_mode`` will be used.
        """
        with open(self.output_filepath, self.__get_open_mode(open_mode)):
            pass

    def write(
            self,
            items: ListSetTuple | Generator[Any, None, None],
            open_mode: OpenMode | None = None,
    ) -> NonNegativeInt:
        """Write items from a list/set/tuple or a generator to a text file, with one item per line.

        Examples of items are product IDs.

        This function opens a text file in the `(over)write` or `append` mode. It then writes each item from the
        provided iterable to the file. It catches specified exceptions during the writing process, and logs them as
        warnings.

        Args:
            items:
                An iterable of items to be written to the file.
            open_mode:
                Defaults to ``None``, which means the value from ``self.open_mode`` will be used.

        Returns:
            The number of items that are written to the file successfully.
        """
        number_of_items_written = 0

        with open(self.output_filepath, self.__get_open_mode(open_mode)) as f:
            for item in items:
                try:
                    item = self.pre_writing_transformation.transform_items(str(item))
                    item = self.pre_writing_transformation.trim_items(item)
                    f.write(item + "\n")
                    number_of_items_written += 1
                except Exception as exception:
                    if self.on_write_catch_exceptions is None:
                        continue
                    if isinstance(exception, self.on_write_catch_exceptions):
                        logger.warning(f"Failed attempt to write {item} to file {self.path}: {exception}")
                    raise exception

        return number_of_items_written

    def write_in_batches(self, batches: Batches, open_mode: OpenMode | None = None) -> NonNegativeInt:
        """Similar to `Writer.write()`_, but assumes that the input is in batches.

        .. _Writer.write(): monkey_wrench.input_output_models.Writer.write
        """
        self.prepare_output_file_for_writing(self.__get_open_mode(open_mode))
        number_of_items_written = 0
        for batch, _ in batches:
            number_of_items_written += self.write(batch, open_mode="a")
        return number_of_items_written


class Reader(ExistingInputFile):
    """Pydantic model for an ASCII file (text mode) reader."""

    post_reading_transformation: StringTransformation = StringTransformation()
    """The transformation after reading items from the file and before returning them.

    Defaults to :obj:`~monkey_wrench.generic.StringTransformation()`, which means the items will be only trimmed.

    Note:
        The items will be first trimmed and then transformed according to
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


class DirectoryVisitor(ParentInputDirectory, Pattern):
    """Pydantic model for visiting files in a directory tree."""

    visitor_writer: Writer | None = None
    """If given, it will be used to write the list of visited files to a text file."""

    visitor_callback: TransformFunction[Any] | None = None
    """A function that will be called every time a match is found for a file. Defaults to ``None``."""

    reverse: bool = False
    """A boolean to determine whether to sort the files in reverse order.

    Defaults to ``False``, which means sorting is in the alphabetical order.
    """

    recursive: bool = True
    """Determines whether to recursively visit the directory tree. or just visit the top-level directory.

    Defaults to ``True``.
    """

    post_visit_transform_function: TransformFunction[ReturnType] | None = None
    """The transform function that will be applied on filepaths after visiting them.

    Defaults to ``None``, which means no transformation is applied.

    Note:
        If it is provided, the result of transformation will be returned instead of filepaths.
    """

    def __collect_files(self) -> list[Path]:
        files_list = []

        if self.recursive:
            for root, _, files in os.walk(self.parent_input_directory_path):
                for file in files:
                    if self.pattern.exists_in(file):
                        files_list.append(Path(root, file))
        else:
            for item in os.listdir(self.parent_input_directory_path):
                if (file := Path(self.parent_input_directory_path, item)).is_file():
                    if self.pattern.exists_in(item):
                        files_list.append(file)

        return sorted(files_list, reverse=self.reverse)

    def visit(self) -> list[ReturnType] | list[Path]:
        """Visit all files in the directory, either recursively or just the top-level files.

        Returns:
            A sorted flat list of all file paths in the given directory that match the given pattern and have been
            treated according to the ``visitor_callback`` function. If the ``post_visit_transform_function`` is provided
            , a list of transformed filepaths will be returned instead.
        """
        files_list = self.__collect_files()

        if self.visitor_callback is not None:
            for f in files_list:
                self.visitor_callback(f)

        if self.visitor_writer is not None:
            self.visitor_writer.write(files_list)

        if self.post_visit_transform_function is not None:
            return [self.post_visit_transform_function(f) for f in files_list]

        return files_list


@validate_call
def validate_items(value: ListSetTuple | Reader | DirectoryVisitor) -> ListSetTuple:
    """Return the items as read from a file, collected from a directory, or simply as they are."""
    match value:
        case Reader():
            return value.read()
        case DirectoryVisitor():
            return value.visit()
        case _:
            return value


Items = Annotated[ListSetTuple | Reader | DirectoryVisitor, AfterValidator(validate_items)]
"""Type annotation and Pydantic validator for a collection of items in any of the following forms.

It can simply be a list/set/tuple of items, or a file reader using which the items can be read, or a directory visitor
which can collect e.g. filepaths.
"""


class FilesIntegrityValidator(MultiProcess):
    """Pydantic model to verify files integrity by checking their size as well as comparing them against a reference.

    Note:
        This class does two main verifications, namely checking for corrupted and missing files as follows

            1- Checking that the file sizes are within some threshold from a nominal file size.
            2- Checking filepaths against a reference collection.
    """

    nominal_file_size: NonNegativeInt | None = None
    """The nominal size of files in bytes. This is used to check for corrupted files.

    Defaults to ``None``, which means the search for corrupted files will not be performed.
    """

    file_size_relative_tolerance: NonNegativeFloat = 0.01
    """The maximum relative difference in the size of a file, before it can be marked as corrupted.

    Defaults to ``0.01``, i.e. any file whose size differs by more than one percent from the nominal size, will be
    marked as corrupted.
    """

    filepath_transform_function: TransformFunction[ReturnType] | None = None
    """A function to transform the file paths into other types of objects before comparing them against the reference.

    This can be e.g. a :func:`~monkey_wrench.date_time.DateTimeParser.parse` function to make datetime objects out of
    file paths. Defaults to ``None`` which means no transformation is performed on the file paths and they will be used
    as they are.
    """

    filepaths: Items
    """The file paths to perform the validation on."""

    reference: Items | None = None
    """Reference items to compare against, used in finding the missing files.

    Defaults to ``None`` which means the search for missing files will not be performed.
    """

    def file_is_corrupted(self, file_size: NonNegativeInt) -> bool:
        return abs(1 - file_size / self.nominal_file_size) > self.file_size_relative_tolerance

    @validate_call
    def find_corrupted_files(self, filepaths: Items | None = None) -> set[Path] | None:
        if filepaths is None:
            filepaths = self.filepaths

        if None in [filepaths, self.nominal_file_size]:
            return None

        file_sizes = self.run_with_results(os.path.getsize, filepaths)
        return {fp for fp, fs in zip(filepaths, file_sizes, strict=True) if self.file_is_corrupted(fs)}

    @validate_call
    def find_missing_files(
            self, filepaths: Items | None = None, reference: Items | None = None
    ) -> set[Path] | None:
        if filepaths is None:
            filepaths = self.filepaths

        if reference is None:
            reference = self.reference

        if None in [reference, filepaths]:
            return None

        if self.filepath_transform_function is not None:
            filepaths = {self.filepath_transform_function(f) for f in filepaths}
        else:
            filepaths = set(filepaths)

        return set(reference) - filepaths

    @validate_call
    def verify_files(
            self, filepaths: Items | None = None, reference: Items | None = None
    ) -> tuple[set[InputType] | set[ReturnType] | None, set[Path] | None]:
        """Check for missing and corrupted files."""
        return self.find_missing_files(filepaths, reference), self.find_corrupted_files(filepaths)


class DateTimeDirectory(ParentOutputDirectory):
    """Pydantic model for datetime directories needed to store products and the input/output of CHIMP."""

    datetime_format_string: str = "%Y/%m/%d"
    """The format string to create subdirectories from the datetime object. Defaults to ``"%Y/%m/%d"``."""

    reset_child_datetime_directory: bool = False
    """Whether to remove the (child) directory first if it already exists. Defaults to ``False``.

    This might save us from issues regarding files being overwritten and corrupted.
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
            ...  parent_output_directory_path=Path.home()
            ... ).get_datetime_directory(
            ...  datetime(2022, 3, 12)
            ... )
            >>> expected_path = Path.home() / Path("2022/03/12")
            >>> expected_path == path
            True
        """
        dir_path = self.parent_output_directory_path / Path(datetime_object.strftime(self.datetime_format_string))
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
            ...  parent_output_directory_path=Path.home()
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
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
