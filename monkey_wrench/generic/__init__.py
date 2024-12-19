"""The package providing some generic utilities and types which will be used in other sub-packages."""

from ._common import apply_to_single_or_all, return_single_or_first
from ._types import Order

__all__ = [
    "Order",
    "apply_to_single_or_all",
    "return_single_or_first",
]
