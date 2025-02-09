from datetime import datetime
from enum import Enum
from os import environ
from typing import ClassVar, Generator, TypeVar

from eumdac import AccessToken
from loguru import logger
from pydantic import HttpUrl, validate_call

from monkey_wrench.date_time import Minutes
from monkey_wrench.generic import Specifications


class CollectionMeta(Specifications):
    """Named tuple to gather the collection metadata."""
    query_string: str
    """A colon (``:``) delimited string which represents the query string for the collection on the EUMETSAT API.

    Example:
        For SEVIRI we have: ``"EO:EUM:DAT:MSG:HRSEVIRI"``.
    """

    snapshot_minutes: Minutes | None = None
    """The minutes for which we have data in an hour.

    Warning:
        For collections that this does not apply, set the default value, i.e. ``None``.

    Example:
        For SEVIRI we have one snapshot per ``15`` minutes, starting from the 12th minute. As a result, we have
        ``[12, 27, 42, 57]`` for SEVIRI snapshots in an hour.
    """


class EumetsatCollection(Enum):
    """Enum class that defines the collections for the EUMETSAT datastore."""
    amsu = CollectionMeta(query_string="EO:EUM:DAT:METOP:AMSUL1")
    avhrr = CollectionMeta(query_string="EO:EUM:DAT:METOP:AVHRRL1")
    mhs = CollectionMeta(query_string="EO:EUM:DAT:METOP:MHSL1")
    seviri = CollectionMeta(query_string="EO:EUM:DAT:MSG:HRSEVIRI", snapshot_minutes=[12, 27, 42, 57])


class EumetsatAPI:
    """Static class for EUMETSAT API functionalities."""
    api_base_url = HttpUrl("https://api.eumetsat.int")
    """The root URL of the EUMETSAT API."""

    download_path_template = "{base}/data/download/1.0.0/collections/{collection}/products"
    """The template URL for the downloading collections."""

    # The following does not include any login credentials, therefore we suppress Ruff linter rule S106.
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

    @staticmethod
    @validate_call
    def make_collection_url(collection: EumetsatCollection) -> HttpUrl:
        """Make a complete collection URL from the API base URL and the given collection (query string).

        Args:
            collection:
                A collection of type :class:`~monkey_wrench.query._types.EumetsatCollection`, e.g. for the SEVIRI we
                have :obj:`EumetsatCollection.seviri`.

        Returns:
            The full collection URL using which the files can be fetched.

        Example:
            >>> EumetsatAPI.make_collection_url(EumetsatCollection.seviri)
            HttpUrl('https://api.eumetsat.int/data/download/1.0.0/collections/EO%3AEUM%3ADAT%3AMSG%3AHRSEVIRI/products')
        """
        return HttpUrl(EumetsatAPI.download_path_template.format(
            base=str(EumetsatAPI.api_base_url).rstrip("/"),
            collection=collection.value.query_string.replace(":", "%3A")
        ))

    @staticmethod
    @validate_call
    def seviri_collection_url() -> HttpUrl:
        """Return the complete URL for the SEVIRI collection."""
        return EumetsatAPI.make_collection_url(EumetsatCollection.seviri)

    @classmethod
    def get_token(cls) -> AccessToken:
        """Get a token using the :obj:`credentials_env_vars`.

        This method returns the same token if it is still valid and issues a new one otherwise.

        Returns:
            A token using which the datastore can be accessed.

        Note:
            See `API key management`_ on the `eumdac` website for more information.

        .. _API key management: https://api.eumetsat.int/api-key
        """
        try:
            credentials = tuple(environ[cls.credentials_env_vars[key]] for key in ["login", "password"])
        except KeyError as error:
            raise KeyError(f"Please set the environment variable {error}.") from None

        token = AccessToken(credentials)

        token_str = str(token)
        token_str = token_str[:3] + " ... " + token_str[-3:]

        logger.info(f"Accessing token '{token_str}' issued at {datetime.now()} and expires {token.expiration}.")
        return token


T = TypeVar("T")
Batches = Generator[tuple[T, int], None, None]
"""Type alias for search results in batches.

For each batch there exists a 2-tuple, in which the first element is the returned items and the second element is the
number of returned items in the same batch.
"""
