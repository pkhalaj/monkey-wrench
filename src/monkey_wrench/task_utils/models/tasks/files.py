"""Module to define Pydantic models for product files tasks."""

from typing import Literal

from pydantic import NonNegativeInt, PositiveFloat, PositiveInt

from monkey_wrench.datetime_utils import FilenameParser, SeviriIDParser
from monkey_wrench.io_utils import (
    collect_files_in_directory,
    compare_files_against_reference,
    read_items_from_txt_file,
    seviri,
)
from monkey_wrench.process_utils import run_multiple_processes
from monkey_wrench.query_utils import EumetsatAPI, List
from monkey_wrench.task_utils.models.specifications.datetime import DateTimeRange
from monkey_wrench.task_utils.models.specifications.paths import Directory, InputFile

from .base import Action, Context, TaskBase


class Task(TaskBase):
    context: Literal[Context.product_files]


class VerifySpecifications(DateTimeRange, InputFile, Directory):
    pattern: list[str] | None = None
    nominal_size: PositiveInt
    tolerance: PositiveFloat


class FetchSpecifications(DateTimeRange, InputFile, Directory):
    number_of_processes: int


class Verify(Task):
    action: Literal[Action.verify]
    specifications: VerifySpecifications

    @TaskBase.log
    def perform(self) -> dict[str, NonNegativeInt]:
        """Verify the product files using the reference."""
        files = List(
            collect_files_in_directory(self.specifications.directory, pattern=self.specifications.pattern),
            FilenameParser
        ).query(
            self.specifications.start_datetime,
            self.specifications.end_datetime
        )

        product_ids = List(
            read_items_from_txt_file(self.specifications.input_filename),
            SeviriIDParser
        ).query(
            self.specifications.start_datetime,
            self.specifications.end_datetime
        )

        datetime_objs = [SeviriIDParser.parse(i) for i in product_ids]
        missing, corrupted = compare_files_against_reference(
            files,
            reference_list=datetime_objs,
            transform_function=FilenameParser.parse,
            nominal_size=self.specifications.nominal_size,
            tolerance=self.specifications.tolerance
        )

        return {
            "number of files found": len(files),
            "number of reference items ": len(datetime_objs),
            "number of missing files": len(missing),
            "number of corrupted files": len(corrupted),
        }


class Fetch(Task):
    action: Literal[Action.fetch]
    specifications: FetchSpecifications

    def fetch(self, product_id: str) -> None:
        """Fetch and resample the file with the given product ID."""
        api = EumetsatAPI()
        fs_file = api.open_seviri_native_file_remotely(product_id, cache="filecache")
        seviri.resample_seviri_native_file(
            fs_file,
            self.specifications.directory,
            seviri.input_filename_from_product_id
        )

    @TaskBase.log
    def perform(self) -> None:
        """Verify the product files using the reference."""
        product_ids = List(
            read_items_from_txt_file(self.specifications.input_filename),
            SeviriIDParser
        ).query(
            self.specifications.start_datetime,
            self.specifications.end_datetime
        )

        run_multiple_processes(self.fetch, product_ids, number_of_processes=self.specifications.number_of_processes)


FilesTask = Fetch | Verify
