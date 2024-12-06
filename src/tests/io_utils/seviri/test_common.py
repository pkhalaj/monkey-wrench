from datetime import datetime
from pathlib import Path

import pytest

from monkey_wrench import io_utils

SAMPLE_PRODUCTS = [
    dict(
        product_id="MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA",
        datetime_object=datetime(2015, 7, 31, 22, 12),
        stamp="20150731_22_12.nc"
    ),
    dict(
        product_id="MSG3-SEVI-MSG15-0100-NA-20150617002739.928000000Z-NA",
        datetime_object=datetime(2015, 6, 17, 0, 27),
        stamp="20150617_00_27.nc"
    )
]


@pytest.mark.parametrize(("prefix", "func", "key"), [
    ("seviri", io_utils.seviri.input_filename_from_product_id, "product_id"),
    ("chimp", io_utils.seviri.output_filename_from_product_id, "product_id"),

    ("seviri", io_utils.seviri.input_filename_from_datetime, "datetime_object"),
    ("chimp", io_utils.seviri.output_filename_from_datetime, "datetime_object")
])
def test_generate_chimp_input_filename_from_product_id(prefix, func, key):
    # single item
    filename = func(SAMPLE_PRODUCTS[0][key])
    assert filename == Path(f"{prefix}_{SAMPLE_PRODUCTS[0]["stamp"]}")

    # list of items
    products = [item[key] for item in SAMPLE_PRODUCTS]
    expected_filenames = [Path(f"{prefix}_{item['stamp']}") for item in SAMPLE_PRODUCTS]
    filenames = func(products)
    assert expected_filenames == filenames
