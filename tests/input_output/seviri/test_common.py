from datetime import datetime
from pathlib import Path

import pytest

from monkey_wrench.input_output.seviri import (
    input_filename_from_datetime,
    input_filename_from_product_id,
    output_filename_from_datetime,
    output_filename_from_product_id,
)

# ======================================================
### Tests for
#             input_filename_from_product_id()
#             output_filename_from_product_id()
#             input_filename_from_datetime()
#             output_filename_from_datetime()

sample_products = [
    dict(
        _product_id="MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
        _datetime=datetime(2015, 7, 31, 22, 12),
        stamp="20150731_22_12.nc"
    ),
    dict(
        _product_id="MSG3-SEVI-MSG15-0100-NA-20150617002739.928000000Z-NA",
        _datetime=datetime(2015, 6, 17, 0, 27),
        stamp="20150617_00_27.nc"
    )
]


@pytest.mark.parametrize(("prefix", "func"), [
    ("seviri", input_filename_from_product_id),
    ("chimp", output_filename_from_product_id),

    ("seviri", input_filename_from_datetime),
    ("chimp", output_filename_from_datetime)
])
def test_generate_chimp_input_output_filename_from_product_id_and_datetime(prefix, func):
    # list of items
    products_attr = products_attribute(func)
    expected_filenames = filename(prefix, sample_products)
    assert expected_filenames == func(products_attr)

    # single items
    for i, attr in enumerate(products_attr):
        assert expected_filenames[i] == func(attr)


def products_attribute(func):
    """Retrieve the desired the attribute based on the function name.

    For example, ``input_filename_from_product_id`` gives ``_product_id`` as the attribute key. It then returns a
    list of all values corresponding to the desired attribute key.
    """
    key = func.__name__.split("from")[-1]
    return [prod[key] for prod in sample_products]


def filename(prefix, product):
    if isinstance(product, list):
        return [filename(prefix, p) for p in product]
    else:
        return Path(f"{prefix}_{product["stamp"]}")
