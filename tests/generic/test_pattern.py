import pytest
from pydantic import BaseModel

from monkey_wrench.generic import Pattern, Strings

# ======================================================
### Tests for Strings()

@pytest.mark.parametrize(("inp", "expected"), [
    ("test", ["test"]),
    (["1", "2"], ["1", "2"]),
    ([], [])
])
def test_Strings(inp, expected):
    class Model(BaseModel):
        field: Strings

    assert expected == Model(field=inp).field


# ======================================================
### Tests for Pattern()

@pytest.mark.parametrize(("kwargs", "res"), [
    (dict(sub_strings=[]), True),
    (dict(sub_strings=""), True),
    (dict(), True),
    (dict(match_all=False), True),
    (dict(case_sensitive=False), True),
    (dict(match_all=False, case_sensitive=False), True),
    #
    (dict(sub_strings="This", match_all=True, case_sensitive=True), True),
    (dict(sub_strings="This", match_all=False, case_sensitive=True), True),
    (dict(sub_strings="This", match_all=False, case_sensitive=False), True),
    (dict(sub_strings="This", match_all=True, case_sensitive=False), True),
    #
    (dict(sub_strings="this", match_all=True, case_sensitive=True), False),
    (dict(sub_strings="this", match_all=False, case_sensitive=True), False),
    (dict(sub_strings="this", match_all=True, case_sensitive=False), True),
    (dict(sub_strings="this", match_all=False, case_sensitive=False), True),
    #
    (dict(sub_strings=["this", "SAMPLE"], match_all=True, case_sensitive=True), False),
    (dict(sub_strings=["this", "SAMPLE"], match_all=True, case_sensitive=False), True),
    (dict(sub_strings=["This", "SAMPLE"], match_all=False, case_sensitive=True), True),
    (dict(sub_strings=["This", "SAMPLE"], match_all=False, case_sensitive=False), True),
    # ,
    (dict(sub_strings=["This", "not"], match_all=False, case_sensitive=True), True),
    (dict(sub_strings=["This", "not"], match_all=False, case_sensitive=False), True),
    (dict(sub_strings=["This", "not"], match_all=True, case_sensitive=True), False),
    (dict(sub_strings=["This", "not"], match_all=True, case_sensitive=False), False),
    #
    (dict(sub_strings=["This", "is", "a", "sample"], match_all=True, case_sensitive=True), True),
    (dict(sub_strings=["This", "is", "a", "not", "sample"], match_all=True, case_sensitive=True), False),
    (dict(sub_strings=["This", "is", "a", "not", "sample"], match_all=False, case_sensitive=True), True),
])
def test_pattern_exist(kwargs, res):
    pattern = Pattern(**kwargs)
    match_function = all if kwargs.get("match_all", pattern.match_all) else any

    assert res is pattern.exists_in("This is a sample!")
    assert res is ("This is a sample!" | pattern)

    assert kwargs.get("case_sensitive", True) is pattern.case_sensitive
    assert kwargs.get("match_all", True) is pattern.match_all
    assert match_function is pattern.match_function
