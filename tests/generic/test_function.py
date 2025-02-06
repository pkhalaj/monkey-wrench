from pathlib import PosixPath

import pytest
from pydantic import ValidationError

from monkey_wrench.generic import Function

# ======================================================
### Tests for Function()

part1 = "input_output"
part2 = "seviri.output_filename_from_product_id"
base = f"{part1}.{part2}"


def test_Function():
    func = Function(path=base)
    assert func("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA") == PosixPath("chimp_20150731_22_12.nc")


@pytest.mark.parametrize("invalid_item", [
    "\\", "/", ":", ";", "-", " ", ">", "<", "=", "%",
    "*", "$", "&", "|", "!", "@", "{", "}",
    "(", ")", "[", "]", "system", "subprocess", ":\b", r"\b"
])
def test_Function_raise_invalid_items(invalid_item):
    with pytest.raises(ValidationError, match="invalid"):
        Function(path=base + invalid_item)

    with pytest.raises(ValidationError, match="invalid"):
        Function(path=invalid_item + base)

    with pytest.raises(ValidationError, match="invalid"):
        Function(path=f"{part1}." + invalid_item + part2)

    with pytest.raises(ValidationError, match="invalid"):
        Function(path=part1 + invalid_item + f".{part2}")


@pytest.mark.parametrize("invalid_item", [
    "..",
    "."
])
def test_Function_raise_leading_trailing(invalid_item):
    with pytest.raises(ValidationError, match="leading/trailing"):
        Function(path=base + invalid_item)

    with pytest.raises(ValidationError, match="leading/trailing"):
        Function(path=invalid_item + base)


@pytest.mark.parametrize("path", [
    f"monkey_wrench.{base}",
    f"{part1}.invalid",
    f"{base}\b"
])
def test_Function_raise_import_fail(path):
    with pytest.raises(ImportError, match="import"):
        Function(path=path)


@pytest.mark.parametrize("path", [
    f"{part1}",
    f"{part1}.seviri.Resampler"
])
def test_Function_raise_not_function(path):
    with pytest.raises(TypeError, match="function"):
        Function(path=path)


def test_Function_raise_not_string():
    from monkey_wrench.input_output.seviri import output_filename_from_product_id as fn
    assert fn("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA") == PosixPath("chimp_20150731_22_12.nc")
    with pytest.raises(ValidationError, match="string"):
        Function(path=fn)
