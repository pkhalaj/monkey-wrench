"""The module which defines utilities for parsing product IDs or filenames into datetime objects."""

import re
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Never

from pydantic import validate_call


class DateTimeParser:
    """Static class for parsing items, e.g. product IDs or filenames, into datetime objects."""

    @staticmethod
    def _raise_value_error(item: Any) -> Never:
        """Helper function to raise a ``ValueError`` when the given item cannot be parsed."""
        raise ValueError(f"Could not parse {item} into a valid datetime object.") from None

    @staticmethod
    @validate_call
    def parse_by_regex(regex_pattern: str, item: str) -> datetime:
        """Parse the given item into a datetime object using regular expression.

        Raises:
            ValueError:
                If the given item cannot be parsed.
        """
        try:
            if match := re.search(regex_pattern, item):
                return datetime(*[int(m) for m in match.groups()])
            raise ValueError()
        except ValueError:
            DateTimeParser._raise_value_error(item)

    @staticmethod
    @validate_call
    def validate_datetime_string(datetime_string: str, datetime_format_string: str) -> datetime:
        """Validate the given datetime string against the given format string.

        Args:
            datetime_string:
                The datetime string to validate.
            datetime_format_string:
                The format string to validate against, e.g. ``"%Y%m%d_%H_%M"``.

        Returns:
            The parsed datetime object, if successful.

        Raises:
            ValueError:
                If the given datetime string cannot be validated or parsed properly.
        """
        try:
            return datetime.strptime(datetime_string, datetime_format_string)
        except ValueError:
            DateTimeParser._raise_value_error(datetime_string)

    @staticmethod
    @abstractmethod
    def parse(item: Any) -> datetime:
        """Parse the given item into a datetime object."""
        pass


class SeviriIDParser(DateTimeParser):
    """Parser class for SEVIRI product IDs."""

    regex_pattern = (r"[0-9A-Za-z]+-SEVI-[0-9A-Za-z]+-[0-9]+-NA"
                     r"-([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})[0-9]{2}\.[0-9]+Z-NA")

    @staticmethod
    @validate_call
    def parse(seviri_product_id: str) -> datetime:
        """Parse the given SEVIRI product ID into a datetime object.

        Example:
            >>> from monkey_wrench.datetime_utils import SeviriIDParser
            >>> valid_Seviri_product_id = "MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA"
            >>> SeviriIDParser.parse()
            datetime.datetime(2015, 7, 31, 22, 12)
        """
        return DateTimeParser.parse_by_regex(SeviriIDParser.regex_pattern, seviri_product_id)


class FilenameParser(DateTimeParser):
    """Parser class for filenames."""

    regex_pattern = r"[0-9A-Za-z]+_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})_([0-9]{2})"

    @staticmethod
    @validate_call
    def parse(filename: Path | str) -> datetime:
        """Parse the given filename into a datetime object.

        The filename can be either the full path or just the basename.

        Example:
            >>> from pathlib import Path
            >>> from monkey_wrench.datetime_utils import FilenameParser
            >>> filename = Path("/home/user/dir/prefix_20150731_22_12.extension")
            >>> FilenameParser.parse(filename)
            datetime.datetime(2015, 7, 31, 22, 12)
        """
        if isinstance(filename, str):
            filename = Path(filename)

        return DateTimeParser.parse_by_regex(FilenameParser.regex_pattern, str(filename.stem))
