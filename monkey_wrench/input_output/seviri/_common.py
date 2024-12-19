"""The module providing utilities for SEVIRI-CHIMP related filename operations."""

from datetime import datetime
from pathlib import Path

from pydantic import validate_call

from monkey_wrench.date_time import SeviriIDParser
from monkey_wrench.generic import apply_to_single_or_all, return_single_or_first

from ._types import ChimpFilesPrefix


@validate_call
def input_filename_from_product_id(product_ids: str | list[str]) -> Path | list[Path]:
    """Generate CHIMP-compliant input filename(s) based on SEVIRI product ID(s).

    Args:
        product_ids:
            Either a single SEVIRI product ID or a list of SEVIRI product IDs.

    Returns:
        Depending on the input, either a single filename or a list of filenames.

    Example:
        >>> from monkey_wrench.input_output.seviri import input_filename_from_product_id
        >>> input_filename_from_product_id("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA")
        'seviri_20150731_22_12.nc'
        >>> input_filename_from_product_id([
        ...  "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
        ...  "MSG3-SEVI-MSG15-0100-NA-20231231171242.800000000Z-NA"
        ... ])
        ['seviri_20150731_22_12.nc', 'seviri_20231231_17_12.nc']
    """
    return __dispatch(ChimpFilesPrefix.seviri, product_ids)


@validate_call
def input_filename_from_datetime(datetime_objects: datetime | list[datetime]) -> Path | list[Path]:
    """Generate CHIMP-compliant input filename(s) based on datetime object(s).

    Args:
        datetime_objects:
            Either a single datetime object or a list of datetime objects.

    Returns:
        Depending on the input, either a single filename or a list of filenames.

    Example:
        >>> from datetime import datetime
        >>> from monkey_wrench.input_output.seviri import input_filename_from_datetime
        >>> input_filename_from_datetime(datetime(2020, 1, 1, 0, 12))
        'seviri_20200101_00_12.nc'
        >>> input_filename_from_datetime([datetime(2020, 1, 1, 0, 12), datetime(2020, 3, 4, 2, 42)])
        ['seviri_20200101_00_12.nc', 'seviri_20200304_02_42.nc']
    """
    return __dispatch(ChimpFilesPrefix.seviri, datetime_objects)


@validate_call
def output_filename_from_product_id(product_ids: str | list[str]) -> Path | list[Path]:
    """Generate CHIMP-compliant output filename(s) based on SEVIRI product ID(s).

    Args:
        product_ids:
            Either a single SEVIRI product ID or a list of SEVIRI product IDs.

    Returns:
        Depending on the input, either a single filename or a list of filenames.

    Example:
        >>> from monkey_wrench.input_output.seviri import output_filename_from_product_id
        >>> output_filename_from_product_id("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA")
        'seviri_20150731_22_12.nc'
        >>> output_filename_from_product_id([
        ...  "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
        ...  "MSG3-SEVI-MSG15-0100-NA-20231231171242.800000000Z-NA"
        ... ])
        ['chimp_20150731_22_12.nc', 'chimp_20231231_17_12.nc']
    """
    return __dispatch(ChimpFilesPrefix.chimp, product_ids)


@validate_call
def output_filename_from_datetime(datetime_objects: datetime | list[datetime]) -> Path | list[Path]:
    """Generate CHIMP-compliant output filename(s) based on datetime object(s).

    Args:
        datetime_objects:
            Either a single datetime object or a list of datetime objects.

    Returns:
        Depending on the input, either a single filename or a list of filenames.

    Example:
        >>> from datetime import datetime
        >>> from monkey_wrench.input_output.seviri import input_filename_from_datetime
        >>> input_filename_from_datetime(datetime(2020, 1, 1, 0, 12))
        'seviri_20200101_00_12.nc'
        >>> input_filename_from_datetime([datetime(2020, 1, 1, 0, 12), datetime(2020, 3, 4, 2, 42)])
        ['chimp_20200101_00_12.nc', 'chimp_20200304_02_42.nc']
    """
    return __dispatch(ChimpFilesPrefix.chimp, datetime_objects)


@validate_call
def __dispatch(
        prefix: ChimpFilesPrefix, single_item_or_list: datetime | str | list[datetime] | list[str]
) -> Path | list[Path]:
    """Dispatch the given input to corresponding CHIMP compliant filename(s) functions."""
    match return_single_or_first(single_item_or_list):
        case datetime():
            return apply_to_single_or_all(
                lambda x: datetime_to_filename(prefix, x), single_item_or_list
            )
        case str():
            return apply_to_single_or_all(
                lambda x: datetime_to_filename(prefix, SeviriIDParser.parse(x)), single_item_or_list
            )


@validate_call
def datetime_to_filename(prefix: ChimpFilesPrefix, datetime_object: datetime, extension: str = ".nc") -> Path:
    """Generate a CHIMP-compliant filename based on the datetime object and the given prefix.

    Args:
        prefix:
            A string with which the filename will start.
        datetime_object:
            The datetime object to retrieve the timestamp string from.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        A filename with the following format ``"<prefix>_<year><month><day>_<hour>_<minute>.extension"``.
    """
    chimp_timestamp_str = datetime_object.strftime("%Y%m%d_%H_%M")
    return Path(f"{prefix.value}_{chimp_timestamp_str}{extension}")
