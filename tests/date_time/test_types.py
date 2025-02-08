import pytest
from pydantic import ValidationError

from monkey_wrench.date_time import Day, Hour, Minute, Minutes, Month, Year
from monkey_wrench.generic import Model

# ======================================================
### Tests for
#               Day()
#               Hour()
#               Minute()
#               Minutes()
#               Month()
#               Year()


@pytest.mark.parametrize(("typ", "min_max"), [
    (Minute, (0, 59)),
    (Day, (1, 31)),
    (Hour, (0, 23)),
    (Month, (1, 12)),
    (Year, (1950, 2100))
])
def test_all_types(typ, min_max):
    mn, mx = min_max

    class Test(Model):
        value: typ

    for v in [mn, mx, (mx + mn) // 2]:
        t = Test(value=v)
        assert t.value == v

    with pytest.raises(ValidationError, match="greater than or equal to"):
        Test(value=mn - 1)

    with pytest.raises(ValidationError, match="less than"):
        Test(value=mx + 1)

    with pytest.raises(ValidationError, match="integer"):
        Test(value=mn + 1.5)


def test_Minutes():
    class Test(Model):
        value: Minutes

    assert Test(value=[1, 2]).value == [1, 2]

    with pytest.raises(ValidationError, match="list"):
        Test(value=1)
