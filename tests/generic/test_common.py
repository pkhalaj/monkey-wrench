from types import NoneType

import pytest

from monkey_wrench.generic import apply_to_single_or_all, get_item_type, pattern_exists


@pytest.mark.parametrize(("pattern", "kwargs", "res"), [
    ("This", dict(match_all=True, case_sensitive=True), True),
    ("This", dict(match_all=False, case_sensitive=True), True),
    ("This", dict(match_all=False, case_sensitive=False), True),
    ("This", dict(match_all=True, case_sensitive=False), True),
    #
    ("this", dict(match_all=True, case_sensitive=True), False),
    ("this", dict(match_all=False, case_sensitive=True), False),
    ("this", dict(match_all=True, case_sensitive=False), True),
    ("this", dict(match_all=False, case_sensitive=False), True),
    #
    (["this", "SAMPLE"], dict(match_all=True, case_sensitive=True), False),
    (["this", "SAMPLE"], dict(match_all=True, case_sensitive=False), True),
    (["This", "SAMPLE"], dict(match_all=False, case_sensitive=True), True),
    (["This", "SAMPLE"], dict(match_all=False, case_sensitive=False), True),
    # ,
    (["This", "not"], dict(match_all=False, case_sensitive=True), True),
    (["This", "not"], dict(match_all=False, case_sensitive=False), True),
    (["This", "not"], dict(match_all=True, case_sensitive=True), False),
    (["This", "not"], dict(match_all=True, case_sensitive=False), False),
    #
    (["This", "is", "a", "sample"], dict(match_all=True, case_sensitive=True), True),
    (["This", "is", "a", "not", "sample"], dict(match_all=True, case_sensitive=True), False),
    (["This", "is", "a", "not", "sample"], dict(match_all=False, case_sensitive=True), True),
])
def _pattern_exist(pattern, kwargs, res):
    assert res == pattern_exists("This is a sample!", pattern, **kwargs)


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
def _apply_to_single_or_all(inp, out):
    assert out == apply_to_single_or_all(lambda x: x ** 2, inp)


@pytest.mark.parametrize(("inp", "out"), [
    ([3, 2, 1], int),
    ((3., 2., 1.), float),
    ("3", str),
    ({1: "a", 2: "b"}, str),
    (None, NoneType),
    (True, bool)
])
def _return_single_or_first(inp, out):
    assert out is get_item_type(inp)


@pytest.mark.parametrize("inp", [
    set(),
    {},
    dict(),
])
def _return_single_or_first_raise(inp):
    with pytest.raises(ValueError, match="Empty"):
        get_item_type(inp)
