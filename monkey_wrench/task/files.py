"""Module to define Pydantic models for tasks related to product files."""
from typing import Any, Literal, TypeVar

from pydantic import Field, NonNegativeInt, model_validator
from typing_extensions import Annotated

from monkey_wrench.date_time import DateTimePeriodStrict, SeviriIDParser
from monkey_wrench.generic import TransformFunction
from monkey_wrench.input_output import FilesIntegrityValidator, Reader, TempDirectory
from monkey_wrench.input_output.seviri import Resampler
from monkey_wrench.process import MultiProcess
from monkey_wrench.query import List
from monkey_wrench.task.base import Action, Context, TaskBase

IntegrityValidatorReturnFieldName = Literal["files", "reference", "corrupted", "missing"]


class FilesTaskBase(TaskBase):
    """Pydantic base model for tasks related to product files."""
    context: Literal[Context.product_files]


class VerifyFilesSpecifications(DateTimePeriodStrict, FilesIntegrityValidator):
    """Pydantic model for the specifications of a verification task."""

    filepath_transform_function: TransformFunction

    verbose: list[IntegrityValidatorReturnFieldName] | bool = False
    """Determines whether the given fields should be reported verbosely, i.e. the actual items will be dumped to the std
    output instead of only the number of items (for the non-verbose mode). It can be a list of field names or a single
    boolean value to change the behaviour for all fields at once.
    """

    @model_validator(mode="before")
    def validate_verbose(cls, data: Any) -> Any:
        """Convert the verbose to a list of field names."""
        match data.get("verbose", False):
            case True:
                data["verbose"] = ["files", "reference", "corrupted", "missing"]
            case False:
                data["verbose"] = []
        return data


class FetchFilesSpecifications(
    DateTimePeriodStrict,
    MultiProcess,
    Resampler,
    Reader,
    TempDirectory
):
    """Pydantic model for the specifications of a fetch task."""
    pass


ElementType = TypeVar("ElementType")


class VerifyFiles(FilesTaskBase):
    """Pydantic model for the verification task."""
    action: Literal[Action.verify]
    specifications: VerifyFilesSpecifications

    def __verbose_or_not(
            self, field: list[ElementType] | set[ElementType], field_name: str
    ) -> NonNegativeInt | list[ElementType] | set[ElementType]:
        if field_name in self.specifications.verbose:
            return field
        return len(field)

    @TaskBase.log
    def perform(self) -> dict[str, NonNegativeInt]:
        """Verify the product files using the reference."""
        files = List(
            self.specifications.filepaths,
            self.specifications.filepath_transform_function
        ).query(
            self.specifications.datetime_period
        ).to_python_list()

        reference = List(
            self.specifications.reference,
        ).query(
            self.specifications.datetime_period
        ).parsed_items.tolist()

        missing, corrupted = self.specifications.verify_files(files, reference)

        return {
            "files found": self.__verbose_or_not(files, "files"),
            "reference items": self.__verbose_or_not(reference, "reference"),
            "missing items": self.__verbose_or_not(missing, "missing"),
            "corrupted files": self.__verbose_or_not(corrupted, "corrupted")
        }


class FetchFiles(FilesTaskBase):
    """Pydantic model for the fetch task."""
    action: Literal[Action.fetch]
    specifications: FetchFilesSpecifications

    @TaskBase.log
    def perform(self) -> None:
        """Fetch the product files."""
        product_ids = List(
            self.specifications.read(),
            SeviriIDParser
        ).query(
            self.specifications.datetime_period
        )

        for product_id in product_ids:
            self.specifications.create_datetime_directory(SeviriIDParser.parse(product_id))

        self.specifications.run(
            self.specifications.resample,
            product_ids.to_python_list(),
            self.specifications.temp_directory_path
        )


FilesTask = Annotated[
    FetchFiles | VerifyFiles,
    Field(discriminator="action")
]
