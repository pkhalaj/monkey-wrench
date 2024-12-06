"""Module to handle SEVIRI-CHIMP related filename operations."""

from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from pydantic import validate_call


@validate_call
def input_filename_from_product_id(product_ids: str | list[str]) -> Path | list[Path]:
    """Generate CHIMP-compliant input filename(s) based on product ID(s)."""
    return __dispatch("seviri", product_ids)


@validate_call
def input_filename_from_datetime(datetime_objects: datetime | list[datetime]) -> Path | list[Path]:
    """Generate CHIMP-compliant input filename(s) based on datetime object(s)."""
    return __dispatch("seviri", datetime_objects)


@validate_call
def output_filename_from_product_id(product_ids: str | list[str]) -> Path | list[Path]:
    """Generate CHIMP-compliant output filename(s) based on product ID(s)."""
    return __dispatch("chimp", product_ids)


@validate_call
def output_filename_from_datetime(datetime_objects: datetime | list[datetime]) -> Path | list[Path]:
    """Generate CHIMP-compliant output filename(s) based on datetime object(s)."""
    return __dispatch("chimp", datetime_objects)


@validate_call
def __apply_all(func: Callable, single_item_or_list: Any) -> Any:
    """Apply the given function on all items of the input (if it is a list), or only on the single input."""
    if isinstance(single_item_or_list, list):
        return [func(i) for i in single_item_or_list]
    return func(single_item_or_list)


@validate_call
def __return_single_item_or_first_from_the_list(single_item_or_list: Any) -> Any:
    """Return the first item from the input if it is a list, otherwise return the input itself."""
    if isinstance(single_item_or_list, list):
        return single_item_or_list[0]
    return single_item_or_list


@validate_call
def __dispatch(prefix: str, single_item_or_list: datetime | str | list[datetime] | list[str]) -> Path | list[Path]:
    """Dispatch the given input to corresponding CHIMP compliant filename(s) functions."""
    match __return_single_item_or_first_from_the_list(single_item_or_list):
        case datetime():
            return __apply_all(
                lambda x: __datetime_to_filename(prefix, x), single_item_or_list
            )
        case str():
            return __apply_all(
                lambda x: __product_id_to_filename(prefix, x), single_item_or_list
            )


@validate_call
def __datetime_to_filename(prefix: str, datetime_object: datetime, extension: str = ".nc") -> Path:
    """Generate a sudo CHIMP-compliant filename based on the datetime object and the given prefix.

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
    return Path(f"{prefix}_{chimp_timestamp_str}{extension}")


@validate_call
def __product_id_to_filename(prefix: str, product_id: str, extension: str = ".nc") -> Path:
    """Similar to :func:`__datetime_to_filename`, but uses the SEVIRI product ID instead.

    Example of such an ID is ``"MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA"``.
    """
    timestamp_str = product_id.split("-")[5][:12]
    return Path(f"{prefix}_{timestamp_str[:8]}_{timestamp_str[8:10]}_{timestamp_str[10:]}{extension}")
