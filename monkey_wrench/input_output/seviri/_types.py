from enum import Enum


class ChimpFilesPrefix(Enum):
    """An enum including all the allowed CHIMP-compliant file prefixes.

    Examples of such prefixes are ``"seviri"`` and ``"chimp"``, where the former marks the input files for CHIMP
    (e.g. ``"seviri_20220112_22_12.nc"`` ) and the latter corresponds to CHIMP output files
    (e.g. ``"chimp_20220112_22_12.nc"``).
    """
    chimp = "chimp"
    seviri = "seviri"
