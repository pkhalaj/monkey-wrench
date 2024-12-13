"""The module that provides metadata related to the EUMETSAT datastore, such as API URLs."""

from enum import Enum
from typing import NamedTuple

from pydantic import HttpUrl, validate_call


class CollectionMeta(NamedTuple):
    """Named tuple to gather the collection metadata."""
    query_string: str
    snapshot_minutes: list[int] | None = None


class EumetsatCollection(Enum):
    """Enum class that defines the collections for the EUMETSAT datastore."""
    amsu = CollectionMeta(query_string="EO:EUM:DAT:METOP:AMSUL1")
    avhrr = CollectionMeta(query_string="EO:EUM:DAT:METOP:AVHRRL1")
    mhs = CollectionMeta(query_string="EO:EUM:DAT:METOP:MHSL1")
    seviri = CollectionMeta(query_string="EO:EUM:DAT:MSG:HRSEVIRI", snapshot_minutes=[12, 27, 42, 57])


class EumetsatAPIUrl:
    """The class that includes the details of the EUMETSAT API URLs."""
    api_base_url = HttpUrl("https://api.eumetsat.int")
    download_path_template = "{base}/data/download/1.0.0/collections/{collection}/products"

    @classmethod
    @validate_call
    def make_collection_url(cls, collection: EumetsatCollection) -> HttpUrl:
        """A class method to make a specific collection URL from the API base URL and the given collection.

        Args:
            collection:
                The collection query string, e.g. for the SEVIRI we have :obj:`EumetsatCollection.seviri`.

        Returns:
            The full collection URL using which the files can be fetched.
        """
        return HttpUrl(cls.download_path_template.format(
            base=str(cls.api_base_url).rstrip("/"),
            collection=collection.value.query_string.replace(":", "%3A")
        ))

    @classmethod
    @validate_call
    def full_seviri_collection_url(cls) -> HttpUrl:
        """Generate the complete URL for the SEVIRI collection."""
        return cls.make_collection_url(EumetsatCollection.seviri)
