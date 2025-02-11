from datetime import UTC, datetime

start_datetime_min = datetime(*[2023, 1, 1, 4, 27], tzinfo=UTC)
end_datetime_max = datetime(*[2022, 12, 31, 20, 42], tzinfo=UTC)
start_datetime = datetime(*[2022, 12, 31, 21, 26], tzinfo=UTC)
end_datetime = datetime(*[2023, 1, 1, 2, 14], tzinfo=UTC)
future_datetime = datetime(*[2200, 10, 27, 0, 0, 30], tzinfo=UTC)
batch_interval = dict(days=2, minutes=1)
output_filepath = "./output_file_which_does_not_exist.txt"

datetime_range_in_batches = dict(
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    batch_interval=batch_interval
)

specifications = dict(
    output_filepath=output_filepath,
    **datetime_range_in_batches
)

task = dict(
    context="ids",
    action="fetch",
    specifications=specifications,
)

ids_in_query = [
    "MSG4-SEVI-MSG15-0100-NA-20230101021243.414000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101015743.524000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101014243.636000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101012743.747000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101011242.652000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101005742.764000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101004242.876000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101002742.988000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101001243.100000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231235743.212000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231234243.324000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231232743.436000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231231243.549000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231225743.661000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231224243.774000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231222742.680000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231221242.793000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231215742.906000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231214243.018000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231212743.131000000Z-NA"
]

ids_out_query = [
    "MSG4-SEVI-MSG15-0100-NA-20230101042743.628000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101041243.738000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101035742.641000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101034242.751000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101032742.861000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101031242.971000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101025743.082000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101024243.192000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20230101022743.303000000Z-NA"
    "MSG4-SEVI-MSG15-0100-NA-20221231211243.244000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231205743.356000000Z-NA",
    "MSG4-SEVI-MSG15-0100-NA-20221231204243.469000000Z-NA"
]

ids = sorted(ids_in_query + ids_out_query, reverse=True)


def task_with(**kwargs):
    _task = {k: v for k, v in task.items()}

    for k in kwargs.keys():
        _task[k] = kwargs[k]

    return _task


def specification_with(**kwargs):
    specs = {k: v for k, v in specifications.items()}

    for k in kwargs.keys():
        specs[k] = kwargs[k]

    return task_with(specifications=specs)
