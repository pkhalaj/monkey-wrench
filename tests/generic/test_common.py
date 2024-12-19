import pytest

from monkey_wrench.generic import apply_to_single_or_all, return_single_or_first


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
    assert apply_to_single_or_all(lambda x: x ** 2, inp) == out


@pytest.mark.parametrize(("inp", "out"), [
    ([3, 2, 1], 3),
    ((3, 2, 1), 3),
    (3, 3),
    ([], []),
    ((), ()),
    (None, None),
    ("abc", "abc")
])
def test_return_single_or_first(inp, out):
    assert return_single_or_first(inp) == out


@pytest.mark.parametrize("inp", [
    set(),
    {1},
    {1, 2, 3},
    {},
    dict(),
    {1: 1},
    {1: 1, 2: 2}
])
def test_return_single_or_first_raise(inp):
    with pytest.raises(ValueError, match="Cannot return"):
        return_single_or_first(inp)
