import pytest

from monkey_wrench.generic import apply_to_single_or_all, return_single_or_first


@pytest.mark.parametrize(("inp", "out"), [
    ([1, 2, 3], [1, 4, 9]),
    ((1, 2, 3), [1, 4, 9]),
    (3, 9),
    ([3], [9]),
    ([], [])
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
])
def test_return_single_or_first(inp, out):
    assert return_single_or_first(inp) == out
