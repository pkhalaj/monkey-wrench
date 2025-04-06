from datetime import datetime

from pydantic import validate_call

from monkey_wrench.date_time import HritFilePathParser
from monkey_wrench.generic import Model
from monkey_wrench.input_output._models import DirectoryVisitor
from monkey_wrench.input_output._types import ExistingFilePath


class HritFilesCollector(Model):
    """Pydantic model to collect and sort HRIT files."""

    hrit_files: list[ExistingFilePath] | DirectoryVisitor
    """A list of filepaths or a directory visitor for the directory containing SEVIRI observation in HRIT format."""

    @property
    @validate_call
    def sorted_files(self) -> dict[datetime, list[ExistingFilePath]]:
        """Get the HRIT files sorted by time.

        It will be returned as a dictionary mapping datetime objects to the corresponding observation files.
        """
        filepaths = self.hrit_files
        if isinstance(filepaths, DirectoryVisitor):
            filepaths = filepaths.visit()
        filepaths = sorted(list(filepaths))

        sorted_filepaths = {}
        for filepath in filepaths:
            sorted_filepaths.setdefault(HritFilePathParser.parse(filepath), []).append(filepath)
        return sorted_filepaths
