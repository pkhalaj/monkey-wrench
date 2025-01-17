"""Module to define Pydantic models for tasks related to product files."""

from typing import Literal

from pydantic import NonNegativeInt

from monkey_wrench.date_time import DateTimeRange, FilePathParser, SeviriIDParser
from monkey_wrench.generic import Pattern
from monkey_wrench.input_output import (
    FileSize,
    InputDirectory,
    InputFile,
    OutputDirectory,
    compare_files_against_reference,
    create_datetime_directory,
    read_items_from_txt_file,
    seviri,
    visit_files_in_directory,
)
from monkey_wrench.input_output.seviri import Resampler
from monkey_wrench.process import run_multiple_processes
from monkey_wrench.query import EumetsatAPI, List
from monkey_wrench.task.base import Action, Context, TaskBase


class Task(TaskBase):
    """Pydantic base model for tasks related to product files."""
    context: Literal[Context.product_files]


class VerifySpecifications(DateTimeRange, FileSize, InputFile, InputDirectory, Pattern):
    """Pydantic model for the specifications of a verification task."""
    recursive: bool = True


class FetchSpecifications(DateTimeRange, InputFile, OutputDirectory, Resampler):
    """Pydantic model for the specifications of a fetch task."""
    number_of_processes: int
    remove_file_if_exists: bool = True,
    save_datasets_options: dict | None = None


class Verify(Task):
    """Pydantic model for the verification task."""
    action: Literal[Action.verify]
    specifications: VerifySpecifications

    @TaskBase.log
    def perform(self) -> dict[str, NonNegativeInt]:
        """Verify the product files using the reference."""
        files = List(
            visit_files_in_directory(
                self.specifications.input_directory,
                pattern=self.specifications.pattern,
                recursive=self.specifications.recursive,
                case_sensitive=self.specifications.case_sensitive,
                match_all=self.specifications.match_all,
            ),
            FilePathParser
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

        datetime_objs = SeviriIDParser.parse_collection(product_ids.to_python_list())
        missing, corrupted = compare_files_against_reference(
            files,
            reference_items=datetime_objs,
            transform_function=FilePathParser.parse,
            nominal_size=self.specifications.nominal_size,
            tolerance=self.specifications.tolerance
        )

        return {
            "number of files found": List.len(files),
            "number of reference items": len(datetime_objs),
            "number of missing files": len(missing),
            "number of corrupted files": len(corrupted),
        }


class Fetch(Task):
    """Pydantic model for the fetch task."""
    action: Literal[Action.fetch]
    specifications: FetchSpecifications

    def fetch(self, product_id: str) -> None:
        """Fetch and resample the file with the given product ID."""
        api = EumetsatAPI()
        fs_file = api.open_seviri_native_file_remotely(product_id, cache=self.specifications.cache)

        datetime_directory = create_datetime_directory(
            SeviriIDParser.parse(product_id),
            parent=self.specifications.output_directory,
            dry_run=True
        )
        seviri.resample_seviri_native_file(
            fs_file,
            datetime_directory,
            seviri.input_filename_from_product_id,
            self.specifications.area,
            radius_of_influence=self.specifications.radius_of_influence,
            remove_file_if_exists=self.specifications.remove_file_if_exists,
            save_datasets_options=self.specifications.save_datasets_options
        )

    @TaskBase.log
    def perform(self) -> None:
        """Fetch the product files."""
        product_ids = List(
            read_items_from_txt_file(self.specifications.input_filename),
            SeviriIDParser
        ).query(
            self.specifications.start_datetime,
            self.specifications.end_datetime
        )

        for product_id in product_ids:
            create_datetime_directory(SeviriIDParser.parse(product_id), parent=self.specifications.output_directory)

        run_multiple_processes(self.fetch, product_ids, number_of_processes=self.specifications.number_of_processes)


FilesTask = Fetch | Verify
