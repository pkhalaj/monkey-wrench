import pytest

from monkey_wrench.generic import Pattern, StringTransformation

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
    match_function = all if kwargs.get("match_all", True) else any
    sub_strings = kwargs.get("sub_strings", pattern.sub_strings)

    assert pattern.exists_in("This is a sample!") is res
    assert ("This is a sample!" | pattern) is res
    assert pattern.sub_strings_list == sub_strings if isinstance(sub_strings, list) else [sub_strings]
    assert pattern.case_sensitive is kwargs.get("case_sensitive", True)
    assert pattern.match_all is kwargs.get("match_all", True)
    assert pattern.match_function is match_function


# ======================================================
### Tests for Trim()

test_string = "test_string"


@pytest.mark.parametrize("inp", [
    test_string,
    [f" {test_string}", f"{test_string} "],
    f" {test_string} ",
    (f" {test_string} \n\t", f"\t\t {test_string} \n\t", f"\t\t {test_string} \n \t \n")
])
def test_Trim(inp):
    assert StringTransformation().trim_items(inp) == expected(inp)
    assert StringTransformation(trim=False).trim_items(inp) == inp
    assert StringTransformation(transform_function=lambda x: str(x).strip()).transform_items(inp) == expected(inp)


def expected(inp):
    match inp:
        case str():
            return test_string
        case list():
            return [test_string] * len(inp)
        case tuple():
            return tuple([test_string] * len(inp))
