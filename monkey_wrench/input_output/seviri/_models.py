"""The module providing a function to read and resample SEVIRI native files from ``FSFile`` objects."""

import os
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Callable
from uuid import uuid4

from fsspec import open_files
from loguru import logger
from pydantic import ConfigDict, NonNegativeInt, validate_call
from satpy import Scene
from satpy.readers.core.seviri import CHANNEL_NAMES
from satpy.readers.core.utils import FSFile

from monkey_wrench.date_time import SeviriIDParser
from monkey_wrench.generic import Function
from monkey_wrench.geometry import Area
from monkey_wrench.input_output._models import DatasetSaveOptions, DateTimeDirectory, FsSpecCache
from monkey_wrench.input_output.seviri._common import input_filename_from_product_id
from monkey_wrench.query import EumetsatAPI

DEFAULT_CHANNEL_NAMES = list(CHANNEL_NAMES.values())
"""Names of SEVIRI channels."""


@contextmanager
def catch_warnings():
    warning_messages = [
        "invalid value encountered in cos*",
        "invalid value encountered in sin*",
        "divide by zero encountered in divide*"
    ]
    with warnings.catch_warnings():
        for message in warning_messages:
            warnings.filterwarnings("ignore", category=RuntimeWarning, message=message)
        yield


class RemoteSeviriFile(FsSpecCache):
    @validate_call
    def open(self, product_id: str) -> FSFile:
        """Open SEVIRI native files (``.nat``) remotely, inside a zip archive using the given product ID.

        Args:
            product_id:
                The product ID to open.

        Returns:
            A file object of type ``FSFile``, which can be further used by ``satpy``.
        """
        https_header = {
            "encoded": True,
            "client_kwargs": {
                "headers": {
                    "Authorization": f"Bearer {EumetsatAPI.get_token()}",
                }
            }
        }
        fstr = f"zip://*.nat{self.fsspec_cache_str}::{EumetsatAPI.seviri_collection_url()}/{product_id}"
        logger.info(f"Opening {fstr}")
        return [FSFile(f) for f in open_files(fstr, https=https_header)][0]


class Resampler(Area, DatasetSaveOptions, DateTimeDirectory, RemoteSeviriFile):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    output_filename_generator: Function[Path] | Callable[[str], Path] = input_filename_from_product_id
    """The function using which an output filename will be generated from the given input filename (SEVIRI native file).

    The generated filename is used to store the resampled file. The generated output filename will be prepended with
    ``output_path`` to compose a complete filepath for the output file.
    """

    channel_names: list[str] = DEFAULT_CHANNEL_NAMES
    """The list of channels to load from the file. Defaults to ``satpy.readers.seviri_base.CHANNEL_NAMES.values()``."""

    radius_of_influence: NonNegativeInt = 20_000
    """An integer which marks the search radius (in meters) for neighbouring data points. Defaults to ``20_000``."""

    remove_file_if_exists: bool = True
    """A boolean to determine whether to removes the output file first if it already exists.

    This might save us from some issues regrading files being overwritten and corrupted.
    """

    @validate_call
    def resample(self, product_id: str) -> None:
        """Resample the given SEVIRI native file (opened with ``fsspec``) using the resampler attributes.

        Args:
            product_id:
                The product ID to open.
        """
        with tempfile.TemporaryDirectory():
            fs_file = self.open(product_id)
            output_directory = self.create_datetime_directory(SeviriIDParser.parse(product_id))
            output_filename = output_directory / self.output_filename_generator(str(fs_file))

            if self.remove_file_if_exists and os.path.exists(output_filename):
                os.remove(output_filename)

            # The ID helps us to quickly find all log messages corresponding to resampling a single file.
            # It is useful in the case of multiprocessing.
            log_id = uuid4()

            logger.info(f"Resampling SEVIRI native file `{fs_file}` to `{output_filename}` -- ID: `{log_id}`")
            scene = Scene([fs_file], "seviri_l1b_native")
            scene.load(self.channel_names)
            resampled_scene = scene.resample(self.area, radius_of_influence=self.radius_of_influence)
            with catch_warnings():
                resampled_scene.save_datasets(filename=str(output_filename), **self.dataset_save_options)
            logger.info(f"Resampling SEVIRI native file `{log_id}` is complete.")
