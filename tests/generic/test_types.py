import pytest
from pydantic import ValidationError

from monkey_wrench.generic import Specifications

# ======================================================
### Tests for Model()

def test_Model():
    class ModelNew(Specifications):
        field: str

    ModelNew(field="test")

    with pytest.raises(ValidationError):
        ModelNew(field="test", another=2)
