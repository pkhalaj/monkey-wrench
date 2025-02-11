from typing import Annotated

from pydantic import Field, NonNegativeInt, PositiveInt

Minute = Annotated[NonNegativeInt, Field(lt=60)]
"""Type annotation and Pydantic validator to represent minutes."""

Minutes = list[Minute]
"""Type alias for a list of minutes."""

Hour = Annotated[NonNegativeInt, Field(lt=24)]
"""Type annotation and Pydantic validator to represent hours."""

Year = Annotated[PositiveInt, Field(ge=1950, le=2100)]
"""Type annotation and Pydantic validator to represent years between 1950 and 2100, inclusive."""

Month = Annotated[PositiveInt, Field(ge=1, le=12)]
"""Type annotation and Pydantic validator to represent one-based numbering of months.

For example, ``1`` corresponds to `January`.
"""

Day = Annotated[PositiveInt, Field(ge=1, le=31)]
"""Type annotation and Pydantic validator to represent one-based numbering of days."""
