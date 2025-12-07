from datetime import UTC, datetime
from pathlib import Path

from satpy.readers.seviri_base import CHANNEL_NAMES

from monkey_wrench.date_time import DateTimePeriod, SeviriIDParser
from monkey_wrench.input_output import Reader
from monkey_wrench.input_output.seviri import Resampler, input_filename_from_product_id
from monkey_wrench.process import MultiProcess
from monkey_wrench.query import List

input_filepath = Path("<replace_with_the_full_path_of_the_text_file_in_which_product_ids_are_stored>")
parent_output_directory_path = Path(
    "<replace_with_the_path_of_the_top_level_directory_where_the_files_are_to_be_stored>"
)

datetime_period = DateTimePeriod(
    start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
    end_datetime=datetime(2024, 1, 1, tzinfo=UTC)
)

area = dict(
    CHIMP_NORDIC_4=dict(
        description="CHIMP region of interest over the nordic countries",
        projection=dict(
            proj="stere",
            lat_0=90,
            lat_ts=60,
            lon_0=14,
            x_0=0,
            y_0=0,
            datum="WGS84",
            no_defs=None,
            type="crs"),
        shape=dict(
            height=564,
            width=452
        ),
        area_extent=dict(
            lower_left_xy=[-745322.8983833211, -3996217.269197446],
            upper_right_xy=[1062901.0232376591, -1747948.2287755085],
            units="m"
        )
    )
)

resampler = Resampler(
    fsspec_cache="filecache",
    radius_of_influence=20_000,
    remove_file_if_exists=True,
    channel_names=list(CHANNEL_NAMES.values()),
    dataset_save_options=dict(
        writer="cf",
        include_lonlats=False
    ),
    parent_output_directory_path=parent_output_directory_path,
    output_filename_generator=input_filename_from_product_id,
    area=area,
)

if __name__ == "__main__":
    product_ids = List(
        Reader(input_filepath=input_filepath).read(),
        SeviriIDParser
    ).query(
        datetime_period
    )

    for product_id in product_ids:
        resampler.create_datetime_directory(SeviriIDParser.parse(product_id))

    MultiProcess(number_of_processes=4).run(
        resampler.resample,
        product_ids.to_python_list(),
    )
