from datetime import datetime, timedelta

import pytest

from monkey_wrench.query import Polygon
from tests.utils import EnvironmentVariables


@pytest.fixture
def api(get_token_or_skip):
    """Get eumetsat api."""
    from monkey_wrench.query import EumetsatAPI, EumetsatCollection
    return EumetsatAPI(EumetsatCollection.amsu)


@pytest.fixture
def search_results(api):
    """Get search results."""
    start = datetime(2021, 1, 1, 0)
    end = datetime(2021, 1, 1, 6)
    # polygon vertices (lon, lat) of small bounding box in central Sweden
    geometry = Polygon(
        vertices=[
            (14.0, 64.0),
            (16.0, 64.0),
            (16.0, 62.0),
            (14.0, 62.0),
            (14.0, 64.0),
        ])
    return api.query(start, end, polygon=geometry)


def test_api_init_raise():
    """Check that the API query raises an exception if the credentials are not set."""
    from monkey_wrench.query import EumetsatAPI
    k1, k2 = EumetsatAPI.credentials_env_vars.values()
    for key1, key2 in [(k1, k2), (k2, k1)]:
        with EnvironmentVariables(**{f"{key1}": "dummy", f"{key2}": None}):
            with pytest.raises(KeyError, match=f"set the environment variable '{key2}'"):
                EumetsatAPI()


def test_api_get_token_success(get_token_or_skip):
    assert get_token_or_skip.expiration > datetime.now()


def test_api_query(get_token_or_skip):
    from monkey_wrench.query import EumetsatAPI
    start_datetime = datetime(2022, 1, 1, )
    end_datetime = datetime(2022, 1, 2)
    assert 96 == EumetsatAPI().query(start_datetime, end_datetime).total_results


def test_api_query_in_batches(get_token_or_skip):
    from monkey_wrench.query import EumetsatAPI, EumetsatCollection

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


def test_fetch_fails(api, search_results, tmp_path):
    nswe_bbox = [64, 62, 114, 116]  # bbox outside the one used for the search query
    outfiles = api.fetch_products(search_results, tmp_path, bounding_box=nswe_bbox, sleep_time=1)
    assert len(outfiles) == 1
    assert outfiles[0] is None


def test_fetch(api, search_results, tmp_path):
    nswe_bbox = [70, 60, 10, 20]
    outfiles = api.fetch_products(search_results, tmp_path, bounding_box=nswe_bbox, sleep_time=1)
    assert len(outfiles) == 1
    assert outfiles[0].is_file()
    assert outfiles[0].suffix == ".nc"


def seviri_product_datetime_is_correct(day: int, product, end_datetime: datetime, start_datetime: datetime):
    """Check that the product datetime is correct."""
    from monkey_wrench.date_time import SeviriIDParser
    datetime_obj = SeviriIDParser.parse(str(product))
    return (start_datetime <= datetime_obj < end_datetime) and (day == datetime_obj.day)


def test_open_seviri_native_remotely(get_token_or_skip):
    from monkey_wrench.query import EumetsatAPI
    product_id = "MSG3-SEVI-MSG15-0100-NA-20230413164241.669000000Z-NA"
    fs_file = EumetsatAPI.open_seviri_native_file_remotely(product_id)
    assert f"{product_id}.nat" == fs_file.open().name
