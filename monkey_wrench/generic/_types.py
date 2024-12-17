from enum import Enum


class Order(Enum):
    """An enum to determine the order of sorting or ordering direction.

    Note:
        Depending on the context, this enum can be interpreted differently. For example, when dealing with a single list
        of filenames, this enum simply corresponds to the alphabetical order of the filenames. However, when querying
        results from the API, this enum specifies the temporal order according to which the results should be returned.
        For example, ``Order.descending`` implies that the latest results should be returned first. Indeed, the two
        interpretations are similar but not exactly the same!
    """
    ascending = 1
    descending = 2
