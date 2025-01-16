"""The module providing Pydantic models for pattern specifications."""

from monkey_wrench.task.models.tasks.base import Specifications


class Pattern(Specifications):
    pattern: list[str] | None = None
    case_sensitive: bool = True
    match_all: bool = True
