"""The module which defines the functions to read and resample SEVIRI native files from ``FSFile`` objects."""

import os
from pathlib import Path
from typing import Callable
from uuid import uuid4

from loguru import logger
from pydantic import DirectoryPath, FilePath
from pyresample import AreaDefinition, load_area
from satpy import Scene
from satpy.readers.seviri_base import CHANNEL_NAMES
from satpy.readers.utils import FSFile

from monkey_wrench.input_output._common import AbsolutePath

DEFAULT_CHANNEL_NAMES = CHANNEL_NAMES.values()
"""Names of SEVIRI channels."""


def resample_seviri_native_file(
        fs_file: FSFile,
        output_directory: AbsolutePath[DirectoryPath],
        output_filename_generator: Callable,
        area: AbsolutePath[FilePath] | AreaDefinition,
        channel_names: list[str] = DEFAULT_CHANNEL_NAMES,
        radius_of_influence: int = 20000,
        remove_file_if_exists: bool = True,
        save_datasets_options: dict | None = None
) -> None:
    """Resample the given SEVIRI native file (opened with ``fsspec``) given an area file and storage options.

    Args:
        fs_file:
            The input file (of type ``FSFile``) to resample.
        output_directory:
            The directory where the output file is to be saved.
        output_filename_generator:
            A function using which an output filename will be generated from the given input filename
            (SEVIRI native file). The generated filename must end in ``".nc"`` and it is used to store the
            resampled file. The generated output filename will be prefixed with ``output_path`` to compose a
            fully-qualified path for the output file.
        area:
            Either a filename (Path) or an object (AreaDefinition) which holds the area information according to which
            the data will be resampled.
        channel_names:
            The list of channels to load from the file. Defaults to
            ``satpy.readers.seviri_base.CHANNEL_NAMES.values()``.
        radius_of_influence:
            An integer which marks the search radius (in meters) for neighbouring data points. Defaults to ``20000``.
        remove_file_if_exists:
            Removes the output file first if it already exists. This might save us from some issues regrading
            files being overwritten and corrupted.
        save_datasets_options:
            Storage options using which the dataset is to be saved. The default behaviour is to use ``cf`` as the writer
            and exclude longitude and latitude values, i.e.
            ``save_datasets_options = dict(writer="cf", include_lonlats=False)``

    Raises:
        ValueError:
            If the generated output filename does not end with ``".nc"``.
    """
    if save_datasets_options is None:
        save_datasets_options = dict(writer="cf", include_lonlats=False)

    match area:
        case AreaDefinition():
            area = area
        case Path():
            area = load_area(area)
        case _:
            raise ValueError(f"Invalid area type: {type(area)}")

    output_filename = output_directory / output_filename_generator(str(fs_file))

    if not str(output_filename).endswith(".nc"):
        raise ValueError(f"The output filename {output_filename_generator(str(fs_file))} does not end with `.nc`.")

    if remove_file_if_exists and os.path.exists(output_filename):
        os.remove(output_filename)

    # The ID helps us to quickly find all log messages corresponding to resampling a single file. It is useful in case
    # of multiprocessing.
    log_id = uuid4()

    logger.info(f"Resampling SEVIRI native file {fs_file} to {output_filename}. ID: {log_id}.")
    scene = Scene([fs_file], "seviri_l1b_native")
    scene.load(channel_names)
    resampled_scene = scene.resample(area, radius_of_influence=radius_of_influence)
    resampled_scene.save_datasets(filename=str(output_filename), **save_datasets_options)
    logger.info(f"Resampling SEVIRI native file {log_id} is complete.")
