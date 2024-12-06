from pydantic import BaseModel


class Specifications(BaseModel, extra="forbid"):
    """Pydantic model for the specifications of a task."""
    pass
