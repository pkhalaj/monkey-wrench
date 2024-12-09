from collections import Counter

from satpy.readers.seviri_base import CHANNEL_NAMES

from monkey_wrench.io_utils.seviri import SEVIRI


def test_channel_names():
    seviri_instance = SEVIRI("seviri")
    assert Counter(CHANNEL_NAMES.values()) == Counter(seviri_instance.variables)
    assert len(CHANNEL_NAMES.values()) == seviri_instance.n_channels
