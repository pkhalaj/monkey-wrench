from pathlib import Path

import pytest
from pydantic import ValidationError

from monkey_wrench.generic import Model, PathLikeType

# ======================================================
### Tests for Model()

def test_Model():
    class ModelNew(Model):
        field: str

    ModelNew(field="test")

    with pytest.raises(ValidationError):
        ModelNew(field="test", another=2)


# ======================================================
### Tests for PathLikeType()

@pytest.fixture
def test_model():
    class Test(Model):
        field: PathLikeType

    return Test


@pytest.mark.parametrize("inp", [
    "path",
    "/home/user/path",
    Path("/home/user/path"),
])
def test_PathLikeType(test_model, inp):
    assert test_model(field=inp).field == Path(inp)


@pytest.mark.parametrize("inp", [
    123,
    []
])
def test_PathLikeType_raise(test_model, inp):
    with pytest.raises(ValidationError, match="cannot be converted"):
        test_model(field=inp)
