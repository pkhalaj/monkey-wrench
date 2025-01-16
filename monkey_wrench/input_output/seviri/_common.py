"""The module providing utilities for SEVIRI-CHIMP related filename operations."""

from datetime import datetime
from pathlib import Path

from pydantic import validate_call

from monkey_wrench.date_time import SeviriIDParser
from monkey_wrench.generic import ListSetTuple, StringOrStrings, apply_to_single_or_collection, element_type
from monkey_wrench.input_output.seviri._types import ChimpFilesPrefix


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
    return __dispatch(ChimpFilesPrefix.seviri, product_ids, extension)


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
    return __dispatch(ChimpFilesPrefix.seviri, datetime_objects, extension)


@validate_call
def output_filename_from_product_id(
        product_ids: StringOrStrings, extension: str = ".nc"
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
    return __dispatch(ChimpFilesPrefix.chimp, product_ids, extension)


@validate_call
def output_filename_from_datetime(
        datetime_objects: datetime | ListSetTuple[datetime], extension: str = ".nc"
) -> Path | ListSetTuple[Path]:
    """Generate (a) CHIMP-compliant output filename(s) based on (a) datetime object(s).

    Args:
        datetime_objects:
            Either a single datetime object , or a list/set/tuple of datetime objects.
        extension:
            The file extension, Defaults to ``".nc"``.

    Returns:
        Depending on the input, either a single filename, or a list/set/tuple of filenames. The type of the
        output matches the type of the input in case of a list/set.tuple, e.g. a tuple of strings as input will result
        in a tuple of paths.

    Example:
        >>> output_filename_from_datetime(datetime(2020, 1, 1, 0, 12))
        PosixPath('chimp_20200101_00_12.nc')

        >>> output_filename_from_datetime(
        ...  [datetime(2020, 1, 1, 0, 12), datetime(2020, 3, 4, 2, 42)]
        ... )
        [PosixPath('chimp_20200101_00_12.nc'), PosixPath('chimp_20200304_02_42.nc')]
    """
    return __dispatch(ChimpFilesPrefix.chimp, datetime_objects)


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
        A filename with the following format ``"<prefix>_<year><month><day>_<hour>_<minute><extension>"``.
    """
    chimp_timestamp_str = datetime_object.strftime("%Y%m%d_%H_%M")
    return Path(f"{prefix.value}_{chimp_timestamp_str}{extension}")


@validate_call
def __dispatch(
        prefix: ChimpFilesPrefix,
        single_item_or_list: datetime | str | ListSetTuple[datetime] | ListSetTuple[str],
        extension: str = ".nc"
) -> Path | list[Path]:
    """Dispatch the given input to its corresponding CHIMP-compliant filename function."""
    tp = element_type(single_item_or_list)
    if tp is datetime:
        return apply_to_single_or_collection(lambda x: datetime_to_filename(prefix, x), single_item_or_list)
    elif tp is str:
        return apply_to_single_or_collection(
            lambda x: datetime_to_filename(prefix, SeviriIDParser.parse(x), extension), single_item_or_list
        )
    else:
        raise TypeError(f"I do not know how to dispatch for type {tp}.")
