from datetime import datetime
from pathlib import Path

import pytest

from monkey_wrench.input_output.seviri import (
    ChimpFilesPrefix,
    input_filename_from_datetime,
    input_filename_from_product_id,
    output_filename_from_datetime,
    output_filename_from_product_id,
)

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
    (ChimpFilesPrefix.seviri, input_filename_from_product_id, "product_id"),
    (ChimpFilesPrefix.chimp, output_filename_from_product_id, "product_id"),

    (ChimpFilesPrefix.seviri, input_filename_from_datetime, "datetime_object"),
    (ChimpFilesPrefix.chimp, output_filename_from_datetime, "datetime_object")
])
def _generate_chimp_input_filename_from_product_id(prefix, func, key):
    # single item
    filename = func(SAMPLE_PRODUCTS[0][key])
    assert Path(f"{prefix.value}_{SAMPLE_PRODUCTS[0]["stamp"]}") == filename

    # list of items
    products = [item[key] for item in SAMPLE_PRODUCTS]
    expected_filenames = [Path(f"{prefix.value}_{item['stamp']}") for item in SAMPLE_PRODUCTS]
    filenames = func(products)
    assert expected_filenames == filenames
