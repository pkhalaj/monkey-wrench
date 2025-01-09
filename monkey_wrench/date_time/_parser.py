"""The module providing utilities for parsing e.g. product IDs or file paths into datetime objects."""

import re
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Never

from pydantic import validate_call


class DateTimeParserBase:
    """A static base class for parsing items, e.g. product IDs or file paths, into datetime objects."""

    @staticmethod
    def _raise_value_error(item: Any) -> Never:
        """Helper function to raise a ``ValueError`` when the given item cannot be parsed."""
        raise ValueError(f"Could not parse {item} into a valid datetime object.") from None

    @staticmethod
    @validate_call
    def parse_by_regex(item: str, regex_pattern: str) -> datetime:
        r"""Parse the given item into a datetime object using a regular expression.

        Args:
            item:
                The item to parse.
            regex_pattern:
                The regular expression to match against the given item.

        Returns:
            The parsed datetime object, if successful.

        Raises:
            ValueError:
                If the given item cannot be parsed.

        Example:
            >>> from monkey_wrench.date_time import DateTimeParserBase
            >>>
            >>> DateTimeParserBase.parse_by_regex(
            ... "20230102_22_30", r"^(19|20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_(0\d|1\d|2[0-3])_([0-5]\d)$")
            datetime.datetime(2023, 1, 2, 22, 30)
        """
        try:
            if match := re.search(regex_pattern, item):
                return datetime(*[int(m) for m in match.groups()])
            raise ValueError()
        except ValueError:
            DateTimeParserBase._raise_value_error(item)

    @staticmethod
    @validate_call
    def parse_by_format_string(datetime_string: str, datetime_format_string: str) -> datetime:
        """Parse the given datetime string into a datetime object using the given format string.

        Args:
            datetime_string:
                The datetime string to parse.
            datetime_format_string:
                The format string using which the parsing is done, e.g. ``"%Y%m%d_%H_%M"``.

        Returns:
            The parsed datetime object, if successful.

        Raises:
            ValueError:
                If the given datetime string cannot be parsed.

        Example:
            >>> from datetime import datetime
            >>> from monkey_wrench.date_time import DateTimeParserBase
            >>>
            >>> DateTimeParserBase.parse_by_format_string("20230101_22_30", "%Y%m%d_%H_%M")
            datetime.datetime(2023, 1, 1, 22, 30)
        """
        try:
            return datetime.strptime(datetime_string, datetime_format_string)
        except ValueError:
            DateTimeParserBase._raise_value_error(datetime_string)

    @staticmethod
    @abstractmethod
    def parse(item: Any) -> datetime:
        """Parse the given item into a datetime object.

        Warning:
            This is an abstract static method and needs to be implemented for each derived class.
        """
        pass


class SeviriIDParser(DateTimeParserBase):
    """Static parser class for SEVIRI product IDs."""

    regex_pattern = (r"[0-9A-Za-z]+-SEVI-[0-9A-Za-z]+-[0-9]+-NA"
                     r"-([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})[0-9]{2}\.[0-9]+Z-NA")

    @staticmethod
    @validate_call
    def parse(seviri_product_id: str) -> datetime:
        """Parse the given SEVIRI product ID into a datetime object.

        Example:
            >>> from monkey_wrench.date_time import SeviriIDParser
            >>>
            >>> SeviriIDParser.parse("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA")
            datetime.datetime(2015, 7, 31, 22, 12)
        """
        return DateTimeParserBase.parse_by_regex(seviri_product_id, SeviriIDParser.regex_pattern)


class FilePathParser(DateTimeParserBase):
    """Static parser class for file paths."""

    regex_pattern = r"[0-9A-Za-z]+_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})_([0-9]{2})"

    @staticmethod
    @validate_call
    def parse(filepath: Path | str) -> datetime:
        """Parse the given filepath into a datetime object.

        Args:
            filepath:
                The filepath to parse. It can be either an absolute path or a relative path (e.g. just the base name).
                For the parsing to be successful, the filepath must have the following format:
                ``<optional_path><prefix>_YYYY_mm_DD_HH_MM<optional_extension>``, where <prefix> is mandatory but can be
                anything except for an empty string. See the examples below.

        Examples:
            >>> from pathlib import Path
            >>> from monkey_wrench.date_time import FilePathParser
            >>>
            >>> # Input is an absolute path of type `Path`.
            >>> FilePathParser.parse(Path("/home/user/dir/prefix_20150731_22_12.extension"))
            datetime.datetime(2015, 7, 31, 22, 12)
            >>> # Input is a relative path of type `Path`.
            >>> FilePathParser.parse(Path("prefix_20150731_22_12.extension"))
            datetime.datetime(2015, 7, 31, 22, 12)
            >>> # Input is an absolute path of type `str`.
            >>> FilePathParser.parse("/home/user/dir/prefix_20150731_22_12.extension")
            datetime.datetime(2015, 7, 31, 22, 12)
            >>> # Input is a relative path of type `str` and does not have an extension.
            >>> FilePathParser.parse("prefix_20150731_22_12")
            datetime.datetime(2015, 7, 31, 22, 12)
            >>> # Input is a relative path of type `str` and its extension is numeric, i.e. `68`.
            >>> FilePathParser.parse("p_20150731_22_1268")
            datetime.datetime(2015, 7, 31, 22, 12)
            >>> # Input is not valid as it is missing the prefix. The following will raise an exception.
            >>> # FilePathParser.parse("20150731_22_12")
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        return DateTimeParserBase.parse_by_regex(str(filepath.stem), FilePathParser.regex_pattern)


DateTimeParser = SeviriIDParser | FilePathParser
