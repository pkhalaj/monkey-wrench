import fnmatch
import shutil
import time
from pathlib import Path
from typing import Generator

from eumdac import DataStore, DataTailor
from eumdac.collection import SearchResults
from eumdac.product import Product
from eumdac.tailor_models import Chain, RegionOfInterest
from loguru import logger
from pydantic import ConfigDict, PositiveInt, validate_call

from monkey_wrench.date_time import (
    DateTimePeriod,
    DateTimeRangeInBatches,
    assert_start_precedes_end,
    floor_datetime_minutes_to_specific_snapshots,
)
from monkey_wrench.geometry import BoundingBox, Polygon
from monkey_wrench.query._base import Query
from monkey_wrench.query._types import EumetsatAPI, EumetsatCollection


class EumetsatQuery(Query):
    @validate_call
    def __init__(
            self, collection: EumetsatCollection = EumetsatCollection.seviri, log_context: str = "EUMETSAT Query"
    ) -> None:
        """Initialize an instance of the class with API credentials read from the environment variables.

        This constructor method sets up a private `eumdac` datastore by obtaining an authentication token using the
        provided API ``login`` and ``password`` which are read from the environment variables.

        Args:
            collection:
                The collection, defaults to :obj:`~monkey_wrench.query._types.EumetsatCollection.seviri` for SEVIRI.
            log_context:
                A string that will be used in log messages to determine the context. Defaults to an empty string.
        """
        super().__init__(log_context=log_context)
        token = EumetsatAPI.get_token()
        self.__collection = collection
        self.__data_store = DataStore(token)
        self.__data_tailor = DataTailor(token)
        self.__selected_collection = self.__data_store.get_collection(collection.value.query_string)

    @staticmethod
    def len(product_ids: SearchResults) -> int:
        """Return the number of product IDs."""
        return product_ids.total_results

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def query(
            self,
            datetime_period: DateTimePeriod,
            polygon: Polygon | None = None,
    ) -> SearchResults:
        """Query product IDs in a single batch.

        This method wraps around the ``eumdac.Collection().search()`` method to perform a search for product IDs
        within a specified time range and the polygon.

        Note:
            For a given SEVIRI collection, an example product ID is
            ``"MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA"``.

        Note:
            ``start_time`` and ``end_time`` are treated respectively as inclusive and exclusive when querying the IDs.
            For example, to obtain all the data up to and including ``2022/12/31``, we must set
            ``end_time=datetime(2023, 1, 1)``.

        Args:
            datetime_period:
                The datetime period to query for.
            polygon:
                An object of type :class:`~monkey_wrench.query._types.Polygon`.

        Returns:
            The results of the search, containing the product IDs found within the specified period and the polygon.

        Raises:
            ValueError:
                Refer to :func:`~monkey_wrench.date_time.assert_start_time_is_before_end_time`.
        """
        assert_start_precedes_end(*datetime_period.as_tuple())
        datetime_period.end_datetime = floor_datetime_minutes_to_specific_snapshots(
            datetime_period.end_datetime, self.__collection.value.snapshot_minutes
        )
        return self.__selected_collection.search(
            dtstart=datetime_period.start_datetime,
            dtend=datetime_period.end_datetime,
            geo=polygon.serialize(as_string=True) if polygon else None
        )

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def query_in_batches(
            self,
            datetime_range_in_batches: DateTimeRangeInBatches
    ) -> Generator[tuple[SearchResults, int], None, None]:
        """Retrieve all the product IDs, given a time range and a batch interval, fetching one batch at a time.

        Args:
            datetime_range_in_batches:
                The datetime range to query for.

        Note:
            As an example, for SEVIRI, we expect to have one file (product ID) per ``15`` minutes, i.e. ``4`` files per
            hour or ``96`` files per day. If our re-analysis period is ``2022/01/01`` (inclusive) to ``2023/01/01``
            (exclusive), i.e. ``365`` days. This results in a maximum of ``35040`` files.

            If we split our datetime range into intervals of ``30`` days and fetch product IDs in batches,
            there is a maximum of ``2880 = 96 x 30`` IDs in each batch retrieved by a single request. One might need to
            adapt this value to avoid running into the issue of sending `too many requests` to the server.

        Yields:
            A generator of 2-tuples. The first element of each tuple is the collection of products retrieved in that
            batch. The second element is the number of the retrieved products for that batch. The search results can be
            in turn iterated over to retrieve individual products.

        Example:
            >>> from datetime import datetime, timedelta, UTC
            >>>
            >>> range_in_batches = DateTimeRangeInBatches(
            ...  start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
            ...  end_datetime=datetime(2022, 1, 3, tzinfo=UTC),
            ...  batch_interval=timedelta(days=1)
            ... )
            >>>
            >>> try:
            ...  api = EumetsatQuery()
            ...  for batch, retrieved_count in api.query_in_batches(range_in_batches):
            ...     assert retrieved_count == batch.total_results
            ...     print(batch)
            ...     for product in batch:
            ...         print(product)
            ... except KeyError as e:  # If the API credentials are not set!
            ...  assert "environment variable" in str(e)
        """
        expected_total_count = self.len(self.query(datetime_range_in_batches.datetime_period))
        yield from super().query_in_batches(
            datetime_range_in_batches,
            expected_total_count=expected_total_count
        )

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def fetch_products(
            self,
            search_results: SearchResults,
            output_directory: Path,
            bounding_box: BoundingBox | None = None,
            output_file_format: str = "netcdf4",
            sleep_time: PositiveInt = 10
    ) -> list[Path | None]:
        """Fetch all products of a search results and write product files to disk.

        Args:
            search_results:
                Search results for which the files will be fetched.
            output_directory:
                The directory to save the files in.
            bounding_box:
                Bounding box, i.e. (north, south, west, east) limits. Defaults to ``None`` which means
                ``BoundingBox(90., -90, -180., 180)`` will be used.
            output_file_format:
                Desired format of the output file(s). Defaults to ``netcdf4``.
            sleep_time:
                Sleep time, in seconds, between requests. Defaults to ``10`` seconds.

        Returns:
            A list paths for the fetched files.
        """
        if not output_directory.exists():
            output_directory.mkdir(parents=True, exist_ok=True)

        if bounding_box is None:
            bounding_box = BoundingBox(90., -90, -180., 180.)

        chain = Chain(
            product=search_results.collection.product_type,
            format=output_file_format,
            roi=RegionOfInterest(NSWE=bounding_box.serialize())
        )
        return [self.fetch_product(product, chain, output_directory, sleep_time) for product in search_results]

    def fetch_product(
            self,
            product: Product,
            chain: Chain,
            output_directory: Path,
            sleep_time: PositiveInt
    ) -> Path | None:
        """Fetch the file for a single product and write the product file to disk.

        Args:
            product:
                The Product whose corresponding file will be fetched.
            chain:
                Chain to apply for customization of the output file.
            output_directory:
                 The directory to save the file in.ort EumetsatAPI
            sleep_time:
                Sleep time, in seconds, between requests.

        Returns:
            The path of the saved file on the disk, Otherwise ``None`` in case of a failure.
        """
        customisation = self.__data_tailor.new_customisation(product, chain)
        logger.info(f"Start downloading product {str(product)}")
        while True:
            if "DONE" in customisation.status:
                customized_file = fnmatch.filter(customisation.outputs, "*.nc")[0]
                with (
                    customisation.stream_output(customized_file) as stream,
                    open(output_directory / stream.name, mode="wb") as fdst
                ):
                    shutil.copyfileobj(stream, fdst)
                    logger.info(f"Wrote file: {fdst.name}' to disk.")
                    return Path(output_directory / stream.name)
            elif customisation.status in ["ERROR", "FAILED", "DELETED", "KILLED", "INACTIVE"]:
                logger.warning(f"Job failed, error code is: '{customisation.status.lower()}'.")
                return None
            elif customisation.status in ["QUEUED", "RUNNING"]:
                logger.info(f"Job is {customisation.status.lower()}.")
                time.sleep(sleep_time)
