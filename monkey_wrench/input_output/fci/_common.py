"""The module providing utilities for FCI-CHIMP related filename operations."""

from datetime import datetime
from pathlib import Path

from pydantic import validate_call

from monkey_wrench.date_time import FCIIDParser
from monkey_wrench.generic import ListSetTuple
from monkey_wrench.input_output._common import __dispatch
from monkey_wrench.query import EumetsatCollection


@validate_call
def input_filename_from_product_id(
        product_ids: str | ListSetTuple[str], extension: str = ".nc"
) -> Path | ListSetTuple[Path]:
    """Generate (a) CHIMP-compliant input filename(s) based on (a)  product ID(s).

    Args:
        product_ids:
            Either a single FCI product ID, or a list/set/tuple of FCI product IDs.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        Depending on the input, either a single filename, or a list/set/tuple of filenames. The type of the
        output matches the type of the input in case of a list/set.tuple, e.g. a tuple of strings as input will result
        in a tuple of paths.

    Example:
        >>> input_filename_from_product_id(
        ...  "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-HRFI-FD--x-x---x_C_EUMT_"
        ...  "20250102102250_IDPFI_OPE_20250102102007_20250102102924_N__O_0063_0000"
        ... )
        PosixPath('fci_20250102_10_20.nc')

        >>> input_filename_from_product_id((
        ...  "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-FDHSI-FD--x-x---x_C_EUMT_"
        ...  "20251231003253_IDPFI_OPE_20251231003007_20251231003928_N__O_0004_0000",
        ...  "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-HRFI-FD--x-x---x_C_EUMT_"
        ...  "20250102102250_IDPFI_OPE_20250102102007_20250102102924_N__O_0063_0000"
        ... ))
        (PosixPath('fci_20251231_00_30.nc'), PosixPath('fci_20250102_10_20.nc'))
    """
    return __dispatch(
        EumetsatCollection.fci_normal_resolution.value.filename_prefix,
        product_ids,
        FCIIDParser,
        extension
    )


@validate_call
def input_filename_from_datetime(
        datetime_objects: datetime | ListSetTuple[datetime], extension: str = ".nc"
) -> Path | ListSetTuple[Path]:
    """Generate (a) CHIMP-compliant input filename(s) based on (a) datetime object(s).

    Args:
        datetime_objects:
            Either a single datetime object, or a list/set/tuple of datetime objects.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        Depending on the input, either a single filename, or a list/set/tuple of filenames. The type of the
        output matches the type of the input in case of a list/set.tuple, e.g. a tuple of strings as input will result
        in a tuple of paths.

    Example:
        >>> input_filename_from_datetime(datetime(2020, 1, 1, 0, 12))
        PosixPath('fci_20200101_00_12.nc')

        >>> input_filename_from_datetime(
        ...  [datetime(2020, 1, 1, 0, 12), datetime(2020, 3, 4, 2, 42)]
        ... )
        [PosixPath('fci_20200101_00_12.nc'), PosixPath('fci_20200304_02_42.nc')]
    """
    return __dispatch(
        EumetsatCollection.fci_normal_resolution.value.filename_prefix,
        datetime_objects,
        None,
        extension
    )


@validate_call
def output_filename_from_product_id(
        product_ids: str | ListSetTuple[str], extension: str = ".nc"
) -> Path | list[Path]:
    """Generate (a) CHIMP-compliant output filename(s) based on (a) FCI product ID(s).

    Args:
        product_ids:
            Either a single FCI product ID , or a list/set/tuple of FCI product IDs.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        Depending on the input, either a single filename, or a list/set/tuple of filenames. The type of the
        output matches the type of the input in case of a list/set.tuple, e.g. a tuple of strings as input will result
        in a tuple of paths.

    Example:
        >>> output_filename_from_product_id(
        ...  "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-HRFI-FD--x-x---x_C_EUMT_"
        ...  "20250102102250_IDPFI_OPE_20250102102007_20250102102924_N__O_0063_0000"
        ... )
        PosixPath('chimp_20250102_10_20.nc')

        >>> output_filename_from_product_id((
        ...  "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-FDHSI-FD--x-x---x_C_EUMT_"
        ...  "20251231003253_IDPFI_OPE_20251231003007_20251231003928_N__O_0004_0000",
        ...  "W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-HRFI-FD--x-x---x_C_EUMT_"
        ...  "20250102102250_IDPFI_OPE_20250102102007_20250102102924_N__O_0063_0000"
        ... ))
        (PosixPath('chimp_20251231_00_30.nc'), PosixPath('chimp_20250102_10_20.nc'))
    """
    return __dispatch(
        "chimp",
        product_ids,
        FCIIDParser,
        extension
    )
