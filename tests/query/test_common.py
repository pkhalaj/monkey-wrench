import pytest

from monkey_wrench.query import Collection, CollectionMeta, EumetsatAPI, EumetsatCollection

base = "https://api.eumetsat.int/data/download/1.0.0/collections"


@pytest.mark.parametrize(("collection", "url"), [
    (EumetsatAPI.seviri_collection_url, "EO%3AEUM%3ADAT%3AMSG%3AHRSEVIRI"),
    (EumetsatAPI.fci_normal_collection_url, "EO%3AEUM%3ADAT%3A0662"),
    (EumetsatAPI.fci_high_collection_url, "EO%3AEUM%3ADAT%3A0665")
])
def test_eumetsat_api_collection_url(collection, url):
    assert collection().unicode_string() == f"{base}/{url}/products"


@pytest.mark.parametrize(("collection", "error_type", "error_message"), [
    (2, ValueError, "Input should be"),
    ("non_existent_collection", ValueError, "Invalid collection"),
    (None, ValueError, "Input should be")
])
def test_collection_fail(collection, error_type, error_message):
    with pytest.raises(error_type, match=error_message):
        Collection(collection=collection)


@pytest.mark.parametrize(("collection", "name"), [
    ("seviri", "seviri"),
    (EumetsatCollection.seviri, "seviri"),
    ("fci_normal_resolution", "fci_normal_resolution"),
    (CollectionMeta(query_string="EO:EUM:DAT:METOP:AMSUL1"), "amsu")
])
def test_collection_success(collection, name):
    c = Collection(collection=collection)
    assert isinstance(c.collection, EumetsatCollection)
    assert c.collection.name == name


def test_eumetsat_collection_all_names():
    assert EumetsatCollection.get_all_names() == [e.name for e in EumetsatCollection]
