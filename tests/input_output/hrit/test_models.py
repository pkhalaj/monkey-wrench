from collections import Counter

import pytest

from monkey_wrench.input_output import DirectoryVisitor
from monkey_wrench.input_output.hrit import HritFilesCollector
from tests.utils import make_dummy_file

from .const import get_datetime_keys, get_files

# ======================================================
### Tests for HritFilesCollector()

@pytest.fixture
def files(temp_dir):
    files = [temp_dir / f for f in get_files()]
    for f in files:
        make_dummy_file(f)
    return files, temp_dir


def test_HritFilesCollector(files):
    files, tmpdir = files

    sorted_files = HritFilesCollector(hrit_files=files).sorted_files
    sorted_files_dir = HritFilesCollector(hrit_files=DirectoryVisitor(parent_input_directory_path=tmpdir)).sorted_files

    assert Counter(sorted_files.keys()) == Counter(get_datetime_keys())
    assert Counter([v for vs in sorted_files.values() for v in vs]) == Counter(files)
    assert sorted_files_dir == sorted_files
