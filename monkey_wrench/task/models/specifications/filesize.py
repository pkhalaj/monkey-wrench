"""The module providing Pydantic models for filesize specifications."""

from pydantic import PositiveFloat, PositiveInt

from monkey_wrench.task.models.tasks.base import Specifications


class FileSize(Specifications):
    nominal_size: PositiveInt
    tolerance: PositiveFloat = 0.01
