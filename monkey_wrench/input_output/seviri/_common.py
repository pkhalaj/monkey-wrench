"""The module providing utilities for SEVIRI-CHIMP related filename operations."""

from datetime import datetime
from pathlib import Path

from pydantic import validate_call

from monkey_wrench.date_time import SeviriIDParser
from monkey_wrench.generic import ListSetTuple
from monkey_wrench.input_output._common import __dispatch
from monkey_wrench.query import EumetsatCollection


@validate_call
def input_filename_from_product_id(
        product_ids: str | ListSetTuple[str], extension: str = ".nc"
) -> Path | ListSetTuple[Path]:
    """Generate (a) CHIMP-compliant input filename(s) based on (a) SEVIRI product ID(s).

    Args:
        product_ids:
            Either a single SEVIRI product ID, or a list/set/tuple of SEVIRI product IDs.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        Depending on the input, either a single filename, or a list/set/tuple of filenames. The type of the
        output matches the type of the input in case of a list/set.tuple, e.g. a tuple of strings as input will result
        in a tuple of paths.

    Example:
        >>> input_filename_from_product_id(
        ...  "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA"
        ... )
        PosixPath('seviri_20150731_22_12.nc')

        >>> input_filename_from_product_id((
        ...  "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
        ...  "MSG3-SEVI-MSG15-0100-NA-20231231171242.800000000Z-NA"
        ... ))
        (PosixPath('seviri_20150731_22_12.nc'), PosixPath('seviri_20231231_17_12.nc'))
    """
    return __dispatch(
        EumetsatCollection.seviri.value.filename_prefix,
        product_ids,
        SeviriIDParser,
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
        PosixPath('seviri_20200101_00_12.nc')

        >>> input_filename_from_datetime(
        ...  [datetime(2020, 1, 1, 0, 12), datetime(2020, 3, 4, 2, 42)]
        ... )
        [PosixPath('seviri_20200101_00_12.nc'), PosixPath('seviri_20200304_02_42.nc')]
    """
    return __dispatch(
        EumetsatCollection.seviri.value.filename_prefix,
        datetime_objects,
        None,
        extension
    )


@validate_call
def output_filename_from_product_id(
        product_ids: str | ListSetTuple[str], extension: str = ".nc"
) -> Path | list[Path]:
    """Generate (a) CHIMP-compliant output filename(s) based on (a) SEVIRI product ID(s).

    Args:
        product_ids:
            Either a single SEVIRI product ID , or a list/set/tuple of SEVIRI product IDs.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        Depending on the input, either a single filename, or a list/set/tuple of filenames. The type of the
        output matches the type of the input in case of a list/set.tuple, e.g. a tuple of strings as input will result
        in a tuple of paths.

    Example:
        >>> output_filename_from_product_id(
        ...  "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA"
        ... )
        PosixPath('chimp_20150731_22_12.nc')

        >>> output_filename_from_product_id([
        ...  "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
        ...  "MSG3-SEVI-MSG15-0100-NA-20231231171242.800000000Z-NA"
        ... ])
        [PosixPath('chimp_20150731_22_12.nc'), PosixPath('chimp_20231231_17_12.nc')]
    """
    return __dispatch(
        "chimp",
        product_ids,
        SeviriIDParser,
        extension
    )
