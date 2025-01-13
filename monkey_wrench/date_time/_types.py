"""The module providing types for the ``date_time`` package."""

from typing import Annotated

from pydantic import Field, NonNegativeInt

Minute = Annotated[NonNegativeInt, Field(lt=60)]
"""Type annotation and Pydantic validator to represent minutes."""

Minutes = list[Minute]
"""Type alias for a list of minutes."""
