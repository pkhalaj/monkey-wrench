"""The module providing common functionalities for the ``query`` package."""

from pydantic import HttpUrl, validate_call

from monkey_wrench.query._types import EumetsatCollection

api_base_url = HttpUrl("https://api.eumetsat.int")
download_path_template = "{base}/data/download/1.0.0/collections/{collection}/products"


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
        >>> from monkey_wrench.query import make_collection_url
        >>>
        >>> make_collection_url(EumetsatCollection.seviri)
        HttpUrl('https://api.eumetsat.int/data/download/1.0.0/collections/EO%3AEUM%3ADAT%3AMSG%3AHRSEVIRI/products')
    """
    return HttpUrl(download_path_template.format(
        base=str(api_base_url).rstrip("/"),
        collection=collection.value.query_string.replace(":", "%3A")
    ))


@validate_call
def seviri_collection_url() -> HttpUrl:
    """Return the complete URL for the SEVIRI collection."""
    return make_collection_url(EumetsatCollection.seviri)
