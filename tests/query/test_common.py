import pytest

from monkey_wrench.query import EumetsatAPI

base = "https://api.eumetsat.int/data/download/1.0.0/collections"


@pytest.mark.parametrize(("collection", "url"), [
    (EumetsatAPI.seviri_collection_url, "EO%3AEUM%3ADAT%3AMSG%3AHRSEVIRI"),
    (EumetsatAPI.fci_normal_collection_url, "EO%3AEUM%3ADAT%3A0662"),
    (EumetsatAPI.fci_high_collection_url, "EO%3AEUM%3ADAT%3A0665")
])
def test_eumetsat_api_collection_url(collection, url):
    assert collection().unicode_string() == f"{base}/{url}/products"
