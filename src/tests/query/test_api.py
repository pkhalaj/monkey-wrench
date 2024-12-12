from datetime import datetime, timedelta
from pathlib import Path

import pytest
from eumdac.collection import SearchResults
from eumdac.product import Product
from eumdac.tailor_models import Chain, RegionOfInterest

from monkey_wrench.date_time import SeviriIDParser
from monkey_wrench.query import EumetsatAPI, EumetsatCollection
from monkey_wrench.test_utils import (
    EnvironmentVariables,
)


@pytest.fixture(scope="session")
def api() -> EumetsatAPI:
    """Get eumetsat api."""
    return EumetsatAPI(EumetsatCollection.amsu)


@pytest.fixture(scope="session")
def search_results(
    api: EumetsatAPI
) -> SearchResults:
    """Get search results."""
    start = datetime(2021, 1, 1, 0)
    end = datetime(2021, 1, 1, 6)
    geometry = [  # polygon vertices (lon, lat) of small bounding box in central Sweden
        (14.0, 64.0),
        (16.0, 64.0),
        (16.0, 62.0),
        (14.0, 62.0),
        (14.0, 64.0),
    ]
    return api.query(start, end, geometry=geometry)


def test_api_init_raise():
    """Check that the API query raises an exception if the credentials are not set."""
    k1, k2 = EumetsatAPI.credentials_env_vars.values()
    for key1, key2 in [(k1, k2), (k2, k1)]:
        with EnvironmentVariables(**{f"{key1}": "dummy", f"{key2}": None}):
            with pytest.raises(KeyError, match=f"set the environment variable '{key2}'"):
                EumetsatAPI()


def test_api_get_token_success(get_token_or_skip):
    assert get_token_or_skip.expiration > datetime.now()


def test_api_query(get_token_or_skip):
    start_datetime = datetime(2022, 1, 1, )
    end_datetime = datetime(2022, 1, 2)
    assert 96 == EumetsatAPI().query(start_datetime, end_datetime).total_results


def test_api_query_in_batches(get_token_or_skip):
    start_datetime = datetime(2022, 1, 1, )
    end_datetime = datetime(2022, 1, 3)
    batch_interval = timedelta(days=1)

    day = 2
    for batch, retrieved_count in EumetsatAPI().query_in_batches(start_datetime, end_datetime, batch_interval):
        assert 96 == batch.total_results
        assert retrieved_count == batch.total_results
        assert EumetsatCollection.seviri.value.query_string == str(batch.collection)

        for product in batch:
            seviri_product_datetime_is_correct(day, product, start_datetime, end_datetime)

        day -= 1

    assert 0 == day


def test_fetch_fails(
    get_token_or_skip,
    api: EumetsatAPI,
    search_results: SearchResults,
    tmp_path: Path,
):
    """Test fetch fails."""
    nswe_bbox = [64, 62, 114, 116]  # bbox outside the one used for the search query
    outfiles = api.fetch(search_results, tmp_path, bbox=nswe_bbox, sleep_time=1)
    assert len(outfiles) == 1 and outfiles[0] is None


def test_fetch(
    get_token_or_skip,
    api: EumetsatAPI,
    search_results: SearchResults,
    tmp_path: Path,
):
    """Test fetch fecthes a product file."""
    nswe_bbox = [64, 62, 14, 16]
    outfiles = api.fetch(search_results, tmp_path, bbox=nswe_bbox, sleep_time=1)
    assert len(outfiles) == 1 and outfiles[0].is_file() and outfiles[0].suffix == "nc"


def seviri_product_datetime_is_correct(day: int, product: Product, end_datetime: datetime, start_datetime: datetime):
    """Check that the product datetime is correct."""
    datetime_obj = SeviriIDParser.parse(str(product))
    return (start_datetime <= datetime_obj < end_datetime) and (day == datetime_obj.day)


def test_open_seviri_native_remotely(get_token_or_skip):
    product_id = "MSG3-SEVI-MSG15-0100-NA-20230413164241.669000000Z-NA"
    fs_file = EumetsatAPI.open_seviri_native_file_remotely(product_id)
    assert f"{product_id}.nat" == fs_file.open().name
