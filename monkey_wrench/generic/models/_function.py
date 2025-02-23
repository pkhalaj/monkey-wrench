import importlib
from functools import lru_cache
from types import FunctionType
from typing import Annotated, Callable, TypeVar

from pydantic import BeforeValidator, validate_call

ReturnType = TypeVar("ReturnType")


@lru_cache(maxsize=1024)
def _import_monkey_wrench_function(function_path: str) -> Callable[..., ReturnType]:
    """Import a function (dynamically) from **Monkey Wrench** using its (string) identifier in the namespace.

    Warning:
        Functions must belong to the **Monkey Wrench** package.

    Args:
        function_path:
            The dot-delimited path of the function in the namespace excluding the leading ``monkey_wrench``. As an
            example to import :func:`monkey_wrench.input_output.seviri.output_filename_from_product_id`, the function
            path must be set to ``input_output.seviri.output_filename_from_product_id``.

    Returns:
        The function that corresponds to the given function path.

    Raises:
        ValueError:
            If ``function_path`` includes any of the invalid items, e.g. ``$`` or ``:``.
        ValueError:
            If ``function_path`` is a relative import path.
        TypeError:
            If ``function_path`` is imported successfully, but it does not point to a function.
        ImportError:
            If ``function_path`` cannot be imported successfully, e.g. it does not exist.
    """
    if function_path.startswith(".") or function_path.endswith("."):
        raise ValueError(
            "The function path cannot include a leading/trailing `.`, i.e. relative imports are not allowed!"
        )

    for item in ("\\", "/", ":", ";", "..", "-", " ", ">", "<", "=", "%", "*", "$", "&", "|", "!", "@", "{", "}",
                 "(", ")", "[", "]", "system", "subprocess"):
        if item in function_path:
            raise ValueError(f"The function path `{function_path}` includes `{item}`, which makes it invalid.")

    try:
        obj = importlib.import_module("monkey_wrench")
        for part in function_path.split("."):
            obj = getattr(obj, part)
    except Exception as e:
        raise ValueError(f"Failed to dynamically import `monkey_wrench.{function_path}`") from e

    if not isinstance(obj, FunctionType):
        raise ValueError(f"{function_path} exists and has been successfully imported, but it is not a function!")

    return obj


@validate_call
def validate_function_path(path: str) -> Callable[..., ReturnType]:
    return _import_monkey_wrench_function(path)


Function = Annotated[Callable[..., ReturnType], BeforeValidator(validate_function_path)]
"""Type annotation and Pydantic validator to dynamically import a function from **Monkey Wrench**, given its path.

Note:
    The path must be a fully qualified namespace path to the function excluding the leading ``monkey_wrench.``.
"""

TransformFunction = Function[ReturnType] | Callable[..., ReturnType]
"""Type annotation for a function that transforms items, e.g. before writing to or after reading from a file."""
