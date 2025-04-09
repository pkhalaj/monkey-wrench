"""The module providing a factory function and a context manager for the ``SEVIRI`` extension.

The extension allows for reading SEVIRI resampled files.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Generator

import numpy as np
from loguru import logger

CHANNEL_NAMES = [
    "HRV",
    "VIS006",
    "VIS008",
    "IR_016",
    "IR_039",
    "WV_062",
    "WV_073",
    "IR_087",
    "IR_097",
    "IR_108",
    "IR_120",
    "IR_134",
]
"""Names of SEVIRI channels.

Warning:
    The order of channels matter. As a result, using ``satpy.readers.seviri_base.CHANNEL_NAMES.values()`` does not
    work! It has the correct channels but not according to the required order!
"""


# The following function embeds a class which makes it too complex.
# Therefore, we supress Ruff linter rule C901.
def _seviri_extension_factory():  # noqa: C901
    """Instantiate a class of type ``SEVIRI``, so that it will be available in the CHIMP namespace."""
    import torch
    import xarray as xr
    from chimp.data import InputDataset
    from chimp.data.utils import scale_slices
    from scipy import ndimage

    class SEVIRI(InputDataset):
        """A derivative class of ``chimp.data.InputDataset`` enabling reading from SEVIRI resampled files."""

        def __init__(self, name: str):
            """The constructor of the class which initializes the instance given a ``name`` for the dataset."""
            super().__init__(name, "seviri", scale=4, variables=CHANNEL_NAMES)

        @property
        def n_channels(self) -> int:
            """Retrieve the number of channels in the dataset."""
            return len(self.variables)

        def load_sample(
                self,
                input_file: Path,
                crop_size: int | tuple[int, int],
                base_scale: int,
                slices: tuple[slice, slice],
                rng: Generator | None = np.random.Generator,
                rotate: float | None = None,
                flip: bool | None = False,
        ) -> torch.Tensor:
            """Load input data sample from file.

            Args:
                input_file:
                    The path of the input file which includes the data.
                crop_size:
                    The size of the final crop.
                base_scale:
                    The scale of the reference data.
                slices:
                    A tuple of slices defining which parts of the data should be loaded.
                rng:
                    A random number generator.
                rotate:
                    If given, it specifies the angle (in degrees) by which the input should be rotated.
                flip:
                    A boolean flag indicating whether to flip the input along the last dimensions.

            Returns:
                A torch tensor containing the loaded input data.
            """
            relative_scale = self.scale / base_scale

            if isinstance(crop_size, int):
                crop_size = (crop_size,) * self.n_dim
            crop_size = tuple((int(size / relative_scale) for size in crop_size))

            x_s = np.full(((self.n_channels,) + crop_size), np.nan)
            if input_file is not None:
                slices = scale_slices(slices, relative_scale)
                try:
                    with xr.open_dataset(input_file) as data:
                        vs = [data[v][dict(zip(self.spatial_dims, slices, strict=True))].data for v in self.variables]
                        x_s = np.stack(vs, axis=0)
                except OSError as e:
                    logger.warning(f"Reading of the input file {input_file} failed. Skipping.\nMore:{e}")

                # Apply augmentations
                if rotate is not None:
                    x_s = ndimage.rotate(
                        x_s, rotate, order=0, reshape=False, axes=(-2, -1), cval=np.nan
                    )
                    height = x_s.shape[-2]

                    # In case of a rotation, we may need to cut off some input.
                    height_out = crop_size[0]
                    if height > height_out:
                        start = (height - height_out) // 2
                        end = start + height_out
                        x_s = x_s[..., start:end, :]

                    width = x_s.shape[-1]
                    width_out = crop_size[1]
                    if width > width_out:
                        start = (width - width_out) // 2
                        end = start + width_out
                        x_s = x_s[..., start:end]

                if flip:
                    x_s = np.flip(x_s, -2)

            return torch.tensor(x_s.copy(), dtype=torch.float32)

    return SEVIRI("seviri")


@contextmanager
def seviri_extension_context() -> Generator[Callable, None, None]:
    """A context manager to load the SEVIRI extension.

    Yields:
        A SEVIRI-aware CHIMP CLI function which can perform a retrieval.
    """
    from chimp import extensions, processing

    from monkey_wrench.chimp import cli

    _original_extension_loader_function = extensions.load
    extensions.load = _seviri_extension_factory
    processing.cli = cli

    try:
        yield processing.cli
    finally:
        extensions.load = _original_extension_loader_function
