"""Common and simple types for the :obj:`monkey_wrench.date_time` package.

Note:
    More specific types (Pydantic models) are defined in :obj:`monkey_wrench.date_time.models``.
"""

from typing import Annotated

from pydantic import Field, NonNegativeInt, PositiveInt

Minute = Annotated[NonNegativeInt, Field(lt=60)]
"""Type annotation and Pydantic validator to represent minutes."""

Minutes = list[Minute]
"""Type alias for a list of minutes."""

Year = Annotated[PositiveInt, Field(ge=1950, le=2100)]
"""Type annotation and Pydantic validator to represent years between 1950 and 2100, inclusive."""

Month = Annotated[PositiveInt, Field(ge=1, le=12)]
"""Type annotation and Pydantic validator to represent one-based numbering of months.

For example, ``1`` corresponds to `January`.
"""

Day = Annotated[PositiveInt, Field(ge=1, le=31)]
"""Type annotation and Pydantic validator to represent one-based numbering of days."""
