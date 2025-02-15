from datetime import UTC, datetime, timedelta

import pytest

from monkey_wrench.date_time import DateTimePeriod, DateTimeRangeInBatches
from monkey_wrench.geometry import BoundingBox, Polygon, Vertex
from tests.utils import EnvironmentVariables


@pytest.fixture
def api(get_token_or_skip):
    """Return an instance of the EUMNETSAT Query, if we can successfully get a token."""
    from monkey_wrench.query import EumetsatCollection, EumetsatQuery
    return EumetsatQuery(EumetsatCollection.amsu)


@pytest.fixture
def search_results(api):
    """Get search results."""
    start = datetime(2021, 1, 1, 0, tzinfo=UTC)
    end = datetime(2021, 1, 1, 6, tzinfo=UTC)

    # polygon vertices (lon, lat) of small bounding box in central Sweden
    geometry = Polygon([
        Vertex(14.0, 64.0),
        Vertex(16.0, 64.0),
        Vertex(16.0, 62.0),
        Vertex(14.0, 62.0),
        Vertex(14.0, 64.0),
    ])
    return api.query(DateTimePeriod(start_datetime=start, end_datetime=end), polygon=geometry)


# ======================================================
### Tests for EumetsatAPI()

def test_EumetsatAPI_raise():
    """Check that the API query raises an exception if the credentials are not set."""
    from monkey_wrench.query import EumetsatAPI
    k1, k2 = EumetsatAPI.credentials_env_vars.values()
    for key1, key2 in [(k1, k2), (k2, k1)]:
        with EnvironmentVariables(**{f"{key1}": "dummy", f"{key2}": None}):
            with pytest.raises(KeyError, match=f"set the environment variable '{key2}'"):
                EumetsatAPI.get_token()


def test_EumetsatAPI_get_token(get_token_or_skip):
    assert get_token_or_skip.expiration > datetime.now()


# ======================================================
### Tests for EumetsatQuery.query()

def test_EumetsatQuery_query(get_token_or_skip):
    from monkey_wrench.query import EumetsatQuery
    datetime_period = DateTimePeriod(
        start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        end_datetime=datetime(2022, 1, 2, tzinfo=UTC)
    )
    assert 96 == EumetsatQuery().query(datetime_period).total_results


# ======================================================
### Tests for EumetsatQuery.query_in_batches()

def test_api_query_in_batches(get_token_or_skip):
    from monkey_wrench.query import EumetsatCollection, EumetsatQuery

    datetime_range_in_batches = DateTimeRangeInBatches(
        start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        end_datetime=datetime(2022, 1, 3, tzinfo=UTC),
        batch_interval=timedelta(days=1)
    )

    day = 2
    for batch, retrieved_count in EumetsatQuery().query_in_batches(datetime_range_in_batches):
        assert 96 == batch.total_results
        assert retrieved_count == batch.total_results
        assert EumetsatCollection.seviri.value.query_string == str(batch.collection)

        for product in batch:
            seviri_product_datetime_is_correct(
                day, product, datetime_range_in_batches.start_datetime, datetime_range_in_batches.end_datetime
            )

        day -= 1

    assert 0 == day


# ======================================================
### Tests for EumetsatQuery.fetch_products()

def test_fetch_product_fail(api, search_results, tmp_path):
    nswe_bbox = BoundingBox(64, 62, 114, 116)  # bbox outside the one used for the search query
    outfiles = api.fetch_products(search_results, tmp_path, bounding_box=nswe_bbox, sleep_time=1)
    assert len(outfiles) == 1
    assert outfiles[0] is None


def test_fetch_product(api, search_results, tmp_path):
    nswe_bbox = BoundingBox(70, 60, 10, 20)
    outfiles = api.fetch_products(search_results, tmp_path, bounding_box=nswe_bbox, sleep_time=1)
    assert len(outfiles) == 1
    if outfiles is not None:  # TODO: Check why this is sometimes `None`.
        assert outfiles[0].is_file()
        assert outfiles[0].suffix == ".nc"


def seviri_product_datetime_is_correct(day: int, product, end_datetime: datetime, start_datetime: datetime):
    """Check that the product datetime is correct."""
    from monkey_wrench.date_time import SeviriIDParser
    datetime_obj = SeviriIDParser.parse(str(product))
    return (start_datetime <= datetime_obj < end_datetime) and (day == datetime_obj.day)
