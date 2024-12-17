import pytest
from pydantic import ValidationError

from monkey_wrench.task.models.specifications.base import Specifications
from monkey_wrench.task.models.specifications.datetime import (
    DateTimeRange,
    DateTimeRangeInBatches,
    EndDateTime,
    StartDateTime,
)
from monkey_wrench.task.models.specifications.paths import OutputFile
from monkey_wrench.task.models.tasks.base import TaskBase
from tests.task.const import BATCH_INTERVAL, END_DATETIME, FUTURE_DATETIME, START_DATETIME


@pytest.mark.parametrize("model", [
    Specifications,
    TaskBase
])
def test_extra_arguments_raise(model):
    with pytest.raises(ValidationError, match="Extra inputs"):
        model(extra_arguments="extra arguments are not allowed!")


@pytest.mark.parametrize(("model", "key"), [
    (StartDateTime, "start_datetime"),
    (EndDateTime, "end_datetime"),
])
def test_start_end_datetime(model, key):
    with pytest.raises(ValidationError, match="should be in the past"):
        model(**{f"{key}": FUTURE_DATETIME})

    with pytest.raises(ValidationError, match="must be a list"):
        model(**{f"{key}": 1})

    with pytest.raises(ValidationError, match="must be integer"):
        model(**{f"{key}": ["A", "B"]})

    with pytest.raises(ValidationError, match="must be positive"):
        model(**{f"{key}": [-1]})


@pytest.mark.parametrize(("model", "extra_arguments"), [
    (DateTimeRange, {}),
    (DateTimeRangeInBatches, dict(batch_interval=BATCH_INTERVAL))
])
def test_datetime_range_start_is_before_end_fail(model, extra_arguments):
    with pytest.raises(ValidationError, match="is later than"):
        model(start_datetime=END_DATETIME, end_datetime=START_DATETIME, **extra_arguments)


@pytest.mark.parametrize(("output_filename", "error_message"), [
    ("./this_is_directory_like/", "cannot end with a '/'"),
    (__file__, "already exists"),
])
def test_output_filename_fail(output_filename, error_message):
    with pytest.raises(ValidationError, match=error_message):
        OutputFile(output_filename=output_filename)
