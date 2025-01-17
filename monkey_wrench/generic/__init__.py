"""The package providing some generic utilities and types which will be used in other sub-packages."""

from ._common import apply_to_single_or_collection, element_type, pattern_exists
from ._models import Pattern, Specifications
from ._types import ListSetTuple, StringOrStrings

__all__ = [
    "ListSetTuple",
    "Pattern",
    "Specifications",
    "StringOrStrings",
    "apply_to_single_or_collection",
    "element_type",
    "pattern_exists"
]
