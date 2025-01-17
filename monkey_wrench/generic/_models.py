from pydantic import BaseModel

from monkey_wrench.generic._types import StringOrStrings


class Specifications(BaseModel, extra="forbid"):
    """Pydantic model for the specifications of a task."""
    pass


class Pattern(Specifications):
    pattern: StringOrStrings | None = None
    case_sensitive: bool = True
    match_all: bool = True
