"""The package providing utilities for resampling FCI files, as well as filename conversions."""

from ._common import (
    input_filename_from_datetime,
    input_filename_from_product_id,
    output_filename_from_product_id,
)

__all__ = [
    "input_filename_from_datetime",
    "input_filename_from_product_id",
    "output_filename_from_product_id",
]
