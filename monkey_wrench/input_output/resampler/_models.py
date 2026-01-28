"""The module providing a function to read and resample files from ``FSFile`` objects."""

import os
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Self
from urllib.parse import quote
from uuid import uuid4

from fsspec import open_files
from loguru import logger
from pydantic import ConfigDict, NonNegativeInt, model_validator, validate_call
from satpy import Scene
from satpy.readers.core.utils import FSFile

from monkey_wrench.geometry import Area
from monkey_wrench.input_output._models import DatasetSaveOptions, DateTimeDirectory, FsSpecCache
from monkey_wrench.input_output.fci._common import input_filename_from_product_id as f_fci
from monkey_wrench.input_output.seviri._common import input_filename_from_product_id as f_seviri
from monkey_wrench.query import Collection, EumetsatAPI, EumetsatCollection

meta = dict(
    seviri=dict(
        output_filename_generator=f_seviri
    ),
    fci_normal_resolution=dict(
        output_filename_generator=f_fci
    )
)


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


class RemoteFile(FsSpecCache):
    @validate_call
    def open(self, product_id: str, temporary_directory: Path, collection: EumetsatCollection) -> list[FSFile]:
        """Open product files remotely, inside a zip archive using the given product ID.

        Args:
            product_id:
                The product ID to open.
            temporary_directory:
                The path where the cache will be stored.
            collection:
                The information about the collection.

        Returns:
            A list of file objects of type ``FSFile``, which can be further used by ``satpy``.
        """
        https_header = {
            "encoded": True,
            "client_kwargs": {
                "headers": {
                    "Authorization": f"Bearer {EumetsatAPI.get_token()}",
                }
            }
        }
        fstr = f"zip://*{collection.value.file_extension}{self.fsspec_cache_str}"
        fstr += f"::{EumetsatAPI.make_collection_url(collection=collection)}/{quote(product_id, safe='')}"
        logger.info(f"Opening {fstr}")
        return [
            FSFile(f) for f in open_files(
                fstr,
                https=https_header,
                filecache={"cache_storage": str(temporary_directory)}
            )
            if "TRAIL" not in str(f)
        ]


class Resampler(Area, Collection, DatasetSaveOptions, DateTimeDirectory, RemoteFile):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    radius_of_influence: NonNegativeInt = 20_000
    """An integer which marks the search radius (in meters) for neighbouring data points. Defaults to ``20_000``."""

    remove_file_if_exists: bool = True
    """A boolean to determine whether to removes the output file first if it already exists.

    This might save us from some issues regrading files being overwritten and corrupted.
    """

    @model_validator(mode="after")
    def validate_output_filename_generator(self) -> Self:  # noqa: N804
        if self.collection.name not in meta.keys():
            raise ValueError(f"Resampling is not implemented for `{self.collection.name}`.")
        return self

    def get_output_filename_generator(self) -> Callable[[str], Path]:
        """Get the function using which an output filename will be generated from the given input filename.

        The generated filename is used to store the resampled file. The generated output filename will be prepended with
        ``output_path`` to compose a complete filepath for the output file.
        """
        return meta[self.collection.name]["output_filename_generator"]

    @validate_call
    def resample(self, product_id: str) -> None:
        """Resample the given file (opened with ``fsspec``) using the resampler attributes.

        Args:
            product_id:
                The product ID to open.
        """
        # The ID helps us to quickly find all log messages corresponding to resampling a single file.
        # It is useful in the case of multiprocessing.
        log_id = uuid4()

        with tempfile.TemporaryDirectory(prefix=f"resample_fsspec_{log_id}_") as temporary_directory:
            fs_files = self.open(product_id, Path(temporary_directory), self.collection)
            output_directory = self.create_datetime_directory(self.collection.value.parser.parse(product_id))
            output_filename = output_directory / self.get_output_filename_generator()(str(fs_files[0]))

            if self.remove_file_if_exists and os.path.exists(output_filename):
                os.remove(output_filename)

            logger.info(
                f"Resampling {self.collection.name} file `{product_id}` to `{output_filename}` -- ID: `{log_id}`"
            )
            scene = Scene(fs_files, self.collection.value.reader)
            scene.load(self.collection.value.channel_names)
            resampled_scene = scene.resample(self.area, radius_of_influence=self.radius_of_influence)
            with catch_warnings():
                resampled_scene.save_datasets(filename=str(output_filename), **self.dataset_save_options)
            logger.info(f"Resampling `{log_id}` is complete.")
