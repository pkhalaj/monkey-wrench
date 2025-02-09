from pathlib import Path

import pytest
from pydantic import DirectoryPath, FilePath, NewPath, ValidationError

from monkey_wrench.generic import Specifications
from monkey_wrench.input_output import AbsolutePath

# ======================================================
### Tests for AbsolutePath()

def test_AbsolutePath_NewPath(empty_task_filepath, temp_dir):
    class Test(Specifications):
        path: AbsolutePath[NewPath]

    with pytest.raises(ValidationError, match="exists"):
        Test(path=empty_task_filepath)

    with pytest.raises(ValidationError, match="exists"):
        Test(path=temp_dir)

    Test(path=temp_dir / Path("non-existent"))


def test_AbsolutePath_DirectoryPath(temp_dir):
    class Test(Specifications):
        path: AbsolutePath[DirectoryPath]

    Test(path=temp_dir)

    with pytest.raises(ValidationError, match="a directory"):
        Test(path=temp_dir / Path("non-existent"))


def test_AbsolutePath_FilePath(empty_task_filepath, temp_dir):
    class Test(Specifications):
        path: AbsolutePath[FilePath]

    Test(path=empty_task_filepath)

    with pytest.raises(ValidationError, match="a file"):
        Test(path=temp_dir / Path("non-existent.txt"))
