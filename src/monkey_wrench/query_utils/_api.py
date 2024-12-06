"""The modules which defines the class for querying the EUMETSAT API."""

from datetime import datetime, timedelta
from os import environ
from typing import Any, ClassVar, Generator

from eumdac import AccessToken, DataStore
from eumdac.collection import SearchResults
from fsspec import open_files
from loguru import logger
from pydantic import ConfigDict, validate_call
from satpy.readers.utils import FSFile

from monkey_wrench.datetime_utils import (
    Order,
    assert_start_time_is_before_end_time,
    floor_datetime_minutes_to_snapshots,
)

from ._common import Query
from ._meta import EumetsatAPIUrl, EumetsatCollection


class EumetsatAPI(Query):
    """A class with utilities to simplify querying all the product IDs from the EUMETSAT API.

    Note:
        This is basically a wrapper around
        `eumdac <https://user.eumetsat.int/resources/user-guides/eumetsat-data-access-client-eumdac-guide>`_.
        However, it does not expose all the functionalities of the ``eumdac``, only the few ones that we need!
    """

    # The following does not include any login credentials, therefore we supress Ruff linter rule S106.
    credentials_env_vars: ClassVar[dict[str, str]] = dict(
        login="EUMETSAT_API_LOGIN",  # noqa: S106
        password="EUMETSAT_API_PASSWORD"  # noqa: S106
    )

    """The keys of environment variables used to authenticate the EUMETSAT API calls.

    Example:
        On Linux, you can use the ``export`` command to set the credentials in a terminal,

        .. code-block:: bash

            export EUMETSAT_API_LOGIN=<login>;
            export EUMETSAT_API_PASSWORD=<password>;
    """

    @validate_call
    def __init__(
            self, collection: EumetsatCollection = EumetsatCollection.seviri, log_context: str = "EUMETSAT API"
    ) -> None:
        """Initialize an instance of the class with API credentials read from the environment variables.

        This constructor method sets up a private ``eumdac`` datastore by obtaining an authentication token using the
        provided API ``login`` and ``password`` which are read from the environment variables.

        Args:
            collection:
                The collection. Defaults to :obj:`EumetsatCollection.seviri` for SEVIRI.
            log_context:
                A string that will be used in log messages to determine the context. Defaults to empty string.

        Note:
            See `API key management <https://api.eumetsat.int/api-key/>`_ on the ``eumdac`` website for more
            information.
        """
        super().__init__(log_context=log_context)
        self.__collection = collection
        self.__datastore = DataStore(EumetsatAPI.get_token())
        self.__selected_collection = self.__datastore.get_collection(collection.value.query_string)

    @classmethod
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def get_token(cls) -> AccessToken:
        """Get a token using the :obj:`credentials_env_vars`.

        This method returns the same token if it is still valid and issues a new one otherwise.

        Returns:
            A token using which the datastore can be accessed.
        """
        try:
            credentials = tuple(environ[cls.credentials_env_vars[key]] for key in ["login", "password"])
        except KeyError as error:
            raise KeyError(f"Please set the environment variable {error}.") from None

        token = AccessToken(credentials)

        token_str = str(token)
        token_str = token_str[:3] + " ... " + token_str[-3:]

        logger.info(f"Access token '{token_str}' issued at {datetime.now()} and expires {token.expiration}")
        return token

    def len(self, product_ids: SearchResults) -> int:
        """Return the number of product IDs."""
        return product_ids.total_results

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def query(self, start_datetime: datetime, end_datetime: datetime) -> SearchResults:
        """Query product IDs in a single batch.

        This method wraps around the ``eumdac.Collection().search()`` method to perform a search for product IDs
        within a specified time range.

        Note:
            For a given SEVIRI collection of ``"EO:EUM:DAT:MSG:HRSEVIRI"``, an example product ID is
            ``"MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA"``.

        Note:
            The keyword arguments of ``start_time`` and ``end_time`` are treated respectively as inclusive and exclusive
            when querying the IDs. For example, to obtain all the data up to and including ``2022/12/31``, we must set
            ``end_time=datetime(2023, 1, 1)``.

        Args:
            start_datetime:
                The start datetime (inclusive).
            end_datetime:
                The end datetime (exclusive).

        Returns:
            The results of the search, containing the product IDs found within the specified time range.

        Raises:
            ValueError:
                Refer to :func:`~monkey_wrench.datetime_utils.assert_start_time_is_before_end_time`.
        """
        assert_start_time_is_before_end_time(start_datetime, end_datetime)
        end_datetime = floor_datetime_minutes_to_snapshots(
            self.__collection.seviri.value.snapshot_minutes, end_datetime
        )
        return self.__selected_collection.search(dtstart=start_datetime, dtend=end_datetime)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def query_in_batches(
            self,
            start_datetime: datetime = datetime(2022, 1, 1),
            end_datetime: datetime = datetime(2023, 1, 1),
            batch_interval: timedelta = timedelta(days=30),
    ) -> Generator[tuple[SearchResults, int], Any, Any]:
        """Retrieve all the product IDs, given a time range and a batch interval, fetching one batch at a time.

        Args:
            start_datetime:
                The start of the datetime range for querying (inclusive). Defaults to January 1, 2022.
            end_datetime:
                The end of the datetime range for querying (exclusive). Defaults to January 1, 2023.
            batch_interval:
                The duration of each batch interval. Defaults to ``30`` days. A smaller value for ``batch_interval``
                means a larger number of batches which increases the overall time needed to fetch all the product IDs.
                A larger value for ``batch_interval`` shortens the total time to fetch all the IDs, however, you might
                get an error regarding sending `too many requests` to the server.

        Note:
            We expect to have one file (product ID) per ``15`` minutes, i.e. ``4`` files per hour or ``96`` files per
            day. For example, suppose our re-analysis period is ``2022/01/01`` (inclusive) to ``2023/01/01``
            (exclusive), i.e. ``365`` days. This results in a maximum of ``35040`` files.

            For example, if we split our datetime range into intervals of ``30`` days and fetch product IDs in batches,
            there is a maximum of ``2880 = 96 x 30`` IDs in each batch retrieved by a single request. One might need to
            adapt this value to avoid running into the issue of sending `too many requests` to the server.

        Yields:
            A generator of tuples. The first element of each tuple is the collection of products retrieved in that
            batch. The second element is the number of the retrieved products for that batch. The search results can be
            in turn iterated over to retrieve individual products.

        Example:
            >>> from datetime import datetime, timedelta
            >>> from monkey_wrench.query_utils import EumetsatAPI
            >>> start_datetime = datetime(2022, 1, 1, )
            >>> end_datetime = datetime(2022, 1, 3)
            >>> batch_interval = timedelta(days=1)
            >>> api = EumetsatAPI()
            >>> for batch, retrieved_count in api.query_in_batches(start_datetime, end_datetime, batch_interval):
            ...     assert retrieved_count == batch.total_results
            ...     print(batch)
            ...     for product in batch:
            ...         print(product)
        """
        expected_total_count = self.len(self.query(start_datetime, end_datetime))
        yield from super().query_in_batches(
            start_datetime,
            end_datetime,
            batch_interval,
            order=Order.decreasing,
            expected_total_count=expected_total_count
        )

    @staticmethod
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def open_seviri_native_file_remotely(product_id: str, cache: str | None = None) -> FSFile:
        """Open SEVIRI native files (``.nat``) remotely, inside a zip archive using the given product ID.

        Note:
            See `fsspec cache <https://filesystem-spec.readthedocs.io/en/latest/features.html#file-buffering-and-random-access>`_,
            to learn more about buffering and random access in `fsspec`.

        Args:
            product_id:
                The product ID to open.
            cache:
                How to buffer, e.g. ``"filecache"``, ``"blockcache"``, or ``None``. Defaults to ``None``.

        Returns:
            A file object of type ``FSFile``, which can be further used by ``satpy``.
        """
        https_header = {
            "encoded": True,
            "client_kwargs": {
                "headers": {
                    "Authorization": f"Bearer {EumetsatAPI.get_token()}",
                }
            }
        }
        cache_str = f"::{cache}" if cache else ""
        fstr = f"zip://*.nat{cache_str}::{EumetsatAPIUrl.full_seviri_collection_url()}/{product_id}"
        logger.info(f"Opening {fstr}")
        return [FSFile(f) for f in open_files(fstr, https=https_header)][0]
