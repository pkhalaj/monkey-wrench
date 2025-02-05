"""The package providing some generic utilities and types, used in other sub-packages of **Monkey Wrench**."""

from ._common import (
    apply_to_single_or_collection,
    assert_,
    element_type,
    element_type_from_collection,
    import_monkey_wrench_function,
)
from ._types import ListSetTuple, Model
from .models import Pattern, Strings

__all__ = [
    "ListSetTuple",
    "Model",
    "Pattern",
    "Strings",
    "apply_to_single_or_collection",
    "assert_",
    "element_type",
    "element_type_from_collection",
    "import_monkey_wrench_function"
]
