from enum import Enum


class WriteMode(Enum):
    """An enum for different write modes."""
    append = "a"
    overwrite = "w"
