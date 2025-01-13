"""The package providing some generic utilities and types which will be used in other sub-packages."""

from ._common import apply_to_single_or_all, get_item_type, pattern_exists
from ._types import ListSetTuple, Order, StringOrStrings

__all__ = [
    "StringOrStrings",
    "ListSetTuple",
    "Order",
    "apply_to_single_or_all",
    "get_item_type",
    "pattern_exists"
]
