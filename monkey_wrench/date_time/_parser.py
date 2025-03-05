import re
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Never
from zoneinfo import ZoneInfo

from pydantic import validate_call

from monkey_wrench.generic import ListSetTuple, apply_to_single_or_collection


class DateTimeParserBase:
    """A static base class for parsing items, e.g. product IDs or file paths, into datetime objects."""

    @staticmethod
    def _raise_value_error(item: Any) -> Never:
        """Helper function to raise a ``ValueError`` when the given item cannot be parsed."""
        raise ValueError(f"Could not parse {item} into a valid datetime object.") from None

    @staticmethod
    @validate_call
    def parse_by_regex(item: str, regex: str, timezone: ZoneInfo | None = None) -> datetime:
        r"""Parse the given item into a datetime object using a regular expression.

        Args:
            item:
                The item to parse.
            regex:
                The regular expression to match against.
            timezone:
                The timezone to add to the datetime object. Defaults to ``None``, which means ``UTC`` will be used.

        Returns:
            The parsed datetime object, if successful.

        Raises:
            ValueError:
                If the given item cannot be parsed.

        Example:
            >>> regex = r"^(19|20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])_(0\d|1\d|2[0-3])_([0-5]\d)$"
            >>> DateTimeParserBase.parse_by_regex("20230102_22_30", regex)
            datetime.datetime(2023, 1, 2, 22, 30, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        if timezone is None:
            timezone = ZoneInfo("UTC")

        try:
            if match := re.search(regex, item):
                return datetime(*[int(m) for m in match.groups()], tzinfo=timezone)
            raise ValueError()
        except ValueError:
            DateTimeParserBase._raise_value_error(item)

    @staticmethod
    @validate_call
    def parse_by_format_string(
            datetime_string: str, datetime_format_string: str, timezone: ZoneInfo | None = None
    ) -> datetime:
        """Parse the given datetime string into a datetime object using the given format string.

        Args:
            datetime_string:
                The datetime string to parse.
            datetime_format_string:
                The format string using which the parsing is done, e.g. ``"%Y%m%d_%H_%M"``.
            timezone:
                The timezone to add to the datetime object. Defaults to ``None``, which means ``UTC`` will be used.

        Returns:
            The parsed datetime object, if successful.

        Raises:
            ValueError:
                If the given datetime string cannot be parsed.

        Example:
            >>> DateTimeParserBase.parse_by_format_string("20230101_22_30", "%Y%m%d_%H_%M")
            datetime.datetime(2023, 1, 1, 22, 30, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        if timezone is None:
            timezone = ZoneInfo("UTC")

        try:
            return datetime.strptime(datetime_string, datetime_format_string).replace(tzinfo=timezone)
        except ValueError:
            DateTimeParserBase._raise_value_error(datetime_string)

    @classmethod
    def parse_collection(
            cls, items: ListSetTuple[Any] | Generator
    ) -> ListSetTuple[datetime] | Generator[datetime, None, None]:
        """Parse the given collection of items into a collection of datetime objects.

        Args:
            items:
                The collection (list/set/tuple or generator) of items to parse.

        Returns:
            A collection of datetime objects. The type of collection matches the type of the input collection, e.g.
            a list as input results in a list of datetime objects.
        """
        return apply_to_single_or_collection(cls.parse, items)

    @staticmethod
    @abstractmethod
    def parse(item: Any) -> datetime:
        """Parse the given item into a datetime object.

        Warning:
            This is an abstract static method and needs to be implemented for each derived class.
        """
        raise NotImplementedError()


class SeviriIDParser(DateTimeParserBase):
    """Static parser class for SEVIRI product IDs."""

    regex = (r"[0-9A-Za-z]+-SEVI-[0-9A-Za-z]+-[0-9]+-NA"
             r"-([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})[0-9]{2}\.[0-9]+Z-NA")

    @staticmethod
    @validate_call
    def parse(seviri_product_id: str) -> datetime:
        """Parse the given SEVIRI product ID into a datetime object.

        Example:
            >>> SeviriIDParser.parse("MSG3-SEVI-MSG15-0100-NA-20150731221240.036000000Z-NA")
            datetime.datetime(2015, 7, 31, 22, 12, tzinfo=zoneinfo.ZoneInfo(key='UTC'))
        """
        return DateTimeParserBase.parse_by_regex(seviri_product_id, SeviriIDParser.regex)


class ChimpFilePathParser(DateTimeParserBase):
    """Static parser class for CHIMP-compiliant input and output file paths."""

    regex = r"[0-9A-Za-z]+_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})_([0-9]{2})"

    @staticmethod
    @validate_call
    def parse(filepath: Path | str) -> datetime:
        """Parse the given filepath into a datetime object.

        Args:
            filepath:
                The filepath to parse. It can be either an absolute path or a relative path (e.g. just the base name).
                For the parsing to be successful, the ``filepath`` must have the following format:
                ``<optional_path><prefix>_<YYYY>_<mm>_<DD>_<HH>_<MM><optional_extension>``, where ``<prefix>`` is
                mandatory but can be anything except for an empty string. See the examples below.

        Examples:
            >>> # Input is an absolute path of type `Path`.
            >>> ChimpFilePathParser.parse(Path("/home/user/dir/seviri_20150731_22_12.extension"))
            datetime.datetime(2015, 7, 31, 22, 12, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is a relative path of type `Path`.
            >>> ChimpFilePathParser.parse(Path("chimp_20150731_22_12.extension"))
            datetime.datetime(2015, 7, 31, 22, 12, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is an absolute path of type `str`.
            >>> ChimpFilePathParser.parse("/home/user/dir/prefix_20150731_22_12.extension")
            datetime.datetime(2015, 7, 31, 22, 12, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is a relative path of type `str` and does not have an extension.
            >>> ChimpFilePathParser.parse("seviri_20150731_22_12")
            datetime.datetime(2015, 7, 31, 22, 12, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is a relative path of type `str` and its extension is numeric, i.e. `72`.
            >>> ChimpFilePathParser.parse("p_20150731_22_1272")
            datetime.datetime(2015, 7, 31, 22, 12, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is invalid (missing prefix). The following will raise an exception!
            >>> # FilePathParser.parse("20150731_22_12")

            >>> # Input is invalid (empty prefix). The following will raise an exception!
            >>> # FilePathParser.parse("_20150731_22_12")
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        return DateTimeParserBase.parse_by_regex(str(filepath.stem), ChimpFilePathParser.regex)


class HritFilePathParser(DateTimeParserBase):
    """Static parser class for HRIT file paths."""

    @staticmethod
    @validate_call
    def parse(filepath: Path | str) -> datetime:
        """Parse the given filepath into a datetime object.

        Args:
            filepath:
                The HRIT filepath to parse. It can be either an absolute path or a relative path
                (e.g. just the base name). For the parsing to be successful, the ``filepath`` must have the following
                format: ``<optional_path><optional_prefix><YYYYmmDDHHMM>-__``. See the examples below.

        Examples:
            >>> # Input is an absolute path of type `Path`.
            >>> HritFilePathParser.parse(
            ...  Path("/home/user/dir/H-000-MSG3__-MSG3________-WV_073___-000008___-202503041900-__")
            ... )
            datetime.datetime(2025, 3, 4, 19, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is a relative path of type `Path`.
            >>> HritFilePathParser.parse(Path("H-000-MSG3__-MSG3________-WV_073___-000008___-202503041900-__"))
            datetime.datetime(2025, 3, 4, 19, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is a relative path of type `str` without a prefix.
            >>> HritFilePathParser.parse(Path("202503041900-__"))
            datetime.datetime(2025, 3, 4, 19, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

            >>> # Input is invalid as it misses the mandatory trailing `-__`. The following will raise an exception!
            >>> # HritFilePathParser.parse(Path("202503041900"))
        """
        if isinstance(filepath, str):
            filepath = Path(filepath)

        return DateTimeParserBase.parse_by_format_string(str(filepath.stem)[-15:-3], "%Y%m%d%H%M")


DateTimeParser = SeviriIDParser | ChimpFilePathParser | HritFilePathParser
