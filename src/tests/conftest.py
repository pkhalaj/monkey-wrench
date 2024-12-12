import tempfile
from pathlib import Path

import pytest
from requests import HTTPError

from monkey_wrench.query import EumetsatAPI


@pytest.fixture
def get_token_or_skip():
    """Attempt to get a valid token and return it. Otherwise, skip the test."""

    def skip(other: str, exc: BaseException) -> None:
        pytest.skip(f"Could not get a valid token. {other}\nMore:{exc}")

    try:
        return EumetsatAPI.get_token()
    except KeyError as e:
        skip("Check that you have correctly set environment variables for the API credentials.", e)
    except HTTPError as e:
        skip("Check that your API credentials are valid.", e)


@pytest.fixture
def temp_dir() -> Path:
    """Make a temporary directory and return it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        yield tmpdir
