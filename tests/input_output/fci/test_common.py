from datetime import datetime
from pathlib import Path

import pytest

from monkey_wrench.input_output.fci import (
    input_filename_from_datetime,
    input_filename_from_product_id,
)

# ======================================================
### Tests for
#             input_filename_from_product_id()
#             output_filename_from_product_id()
#             input_filename_from_datetime()

sample_products = [
    dict(
        _product_id="W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-HRFI-FD--x-x---x_C_EUMT_"
                    "20250102230305_IDPFI_OPE_20250102230007_20250102230924_N__O_0139_0000",
        _datetime=datetime(2025, 1, 2, 23, 0),
        stamp="20250102_23_00.nc"
    ),
    dict(
        _product_id="W_XX-EUMETSAT-Darmstadt,IMG+SAT,MTI1+FCI-1C-RRAD-FDHSI-FD--x-x---x_C_"
                    "EUMT_20251231032247_IDPFI_OPE_20251231032007_20251231032928_N__O_0021_0000",
        _datetime=datetime(2025, 12, 31, 3, 20),
        stamp="20251231_03_20.nc"
    )
]


@pytest.mark.parametrize(("prefix", "func"), [
    ("fci", input_filename_from_product_id),
    ("fci", input_filename_from_datetime),
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
