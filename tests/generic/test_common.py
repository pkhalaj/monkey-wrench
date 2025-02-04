from types import NoneType

import pytest

from monkey_wrench.generic import apply_to_single_or_collection, assert_, element_type, element_type_from_collection

# ======================================================
### Tests for assert_()

@pytest.mark.parametrize(("inp", "out"), [
    (1, 1),
    (True, True),
    (False, False),
    (5 > 3, True),
    ({}, False)
])
def test_assert_(inp, out):
    assert out == assert_(inp, "")


@pytest.mark.parametrize(("inp", "msg", "exception"), [
    (0, "fail", TypeError),
    ([], "fail2", ValueError),
])
def test_assert_raise(inp, msg, exception):
    with pytest.raises(exception, match=msg):
        assert_(inp, msg, silent=False, exception=exception)


# ======================================================
### Tests for apply_to_single_or_collection()

@pytest.mark.parametrize(("inp", "out"), [
    ([1, 2, 3], [2, 4, 6]),
    ((1, 2, 3), (2, 4, 6)),
    ({1, 2, 3}, {2, 4, 6}),
    (3, 6),
    ([3], [6]),
    ([], []),
    ({}, {}),
    (tuple(), tuple()),
    ({"a": 1, "b": 2}, {"a": 2, "b": 4}),
    ("book", "bookbook")
])
def test_apply_to_single_or_collection(inp, out):
    assert out == apply_to_single_or_collection(lambda x: x * 2, inp)


# ======================================================
### Tests for element_type_from_collection()

@pytest.mark.parametrize(("inp", "out"), [
    ([3, 2, 1], int),
    ((3., 2., 1.), float),
    ({1: "a", 2: "b"}, str),
])
def test_element_type_from_collection(inp, out):
    assert out is element_type_from_collection(inp)


@pytest.mark.parametrize("inp", [
    set(),
    dict(),
    list(),
    tuple()
])
def test_element_type_from_collection_empty(inp):
    assert element_type_from_collection(inp) is None


@pytest.mark.parametrize(("inp", "msg", "exception"), [
    ([3, 2., 1], "different", TypeError),
    ({3, "2"}, "different", TypeError),
    (1, "a valid", ValueError),
])
def test_element_type_from_collection_raise(inp, msg, exception):
    with pytest.raises(exception, match=msg):
        element_type_from_collection(inp)


# ======================================================
### Tests for element_type()

@pytest.mark.parametrize(("inp", "out"), [
    ([3, 2, 1], int),
    ((3., 2., 1.), float),
    ("3", str),
    ("", str),
    ({1: "a", 2: "b"}, str),
    (None, NoneType),
    (True, bool)
])
def test_element_type(inp, out):
    assert out is element_type(inp)


@pytest.mark.parametrize("inp", [
    set(),
    dict(),
    list(),
    tuple()
])
def test_element_type_empty(inp):
    assert element_type(inp) is None
