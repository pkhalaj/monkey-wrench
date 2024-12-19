from types import NoneType

import pytest

from monkey_wrench.generic import apply_to_single_or_all, get_item_type


@pytest.mark.parametrize(("inp", "out"), [
    ([1, 2, 3], [1, 4, 9]),
    ((1, 2, 3), (1, 4, 9)),
    ({1, 2, 3}, {1, 4, 9}),
    (3, 9),
    ([3], [9]),
    ([], []),
    ({}, {}),
    (tuple(), tuple()),
    ({"a": 1, "b": 2}, {"a": 1, "b": 4})
])
def test_apply_to_single_or_all(inp, out):
    assert out == apply_to_single_or_all(lambda x: x ** 2, inp)


@pytest.mark.parametrize(("inp", "out"), [
    ([3, 2, 1], int),
    ((3., 2., 1.), float),
    ("3", str),
    ({1: "a", 2: "b"}, str),
    (None, NoneType),
    (True, bool)
])
def test_return_single_or_first(inp, out):
    assert out is get_item_type(inp)


@pytest.mark.parametrize("inp", [
    set(),
    {},
    dict(),
])
def test_return_single_or_first_raise(inp):
    with pytest.raises(ValueError, match="Empty"):
        get_item_type(inp)
