from pathlib import Path

import fsspec
from loguru import logger


def remote_file(path):
    tmp = fsspec.open(path).open()

    def is_dir(*_args): return False

    def match(*_args): return True

    tmp.is_dir = is_dir
    tmp.match = match
    tmp.stem = path.split("/")[-1].split(".")[0]
    tmp.__str__ = str(path)
    return tmp


def cli(
        model: Path,
        input_datasets: list[str],
        input_paths: list[str],
        output_path: str,
        device: str = "cuda",
        precision: str = "single",
        tile_size: int = 128,
        sequence_length: int = 0,
        temporal_overlap: int = 8,
        forecast: int = 0
) -> int:
    from pathlib import Path

    import torch
    from chimp.data.input import (
        InputLoader,
        SequenceInputLoader,
    )
    from chimp.processing import retrieval_step
    from pansat.time import to_datetime
    from pytorch_retrieve.architectures import load_model

    if forecast > 0:
        raise NotImplementedError("Forecast mode is not yet supported in Monkey Wrench!")

    input_path = [remote_file(i) for i in input_paths]

    input_datasets = input_datasets.split(",")
    if sequence_length < 2:
        input_data = InputLoader(input_path, input_datasets)
        temporal_overlap = 0
    else:
        if temporal_overlap is None:
            temporal_overlap = sequence_length - 1
        input_data = SequenceInputLoader(
            input_path,
            input_datasets,
            sequence_length=sequence_length,
            forecast=forecast,
            temporal_overlap=temporal_overlap
        )
    model = load_model(model)

    output_path = Path(output_path)
    if not output_path.exists():
        output_path.mkdir(parents=True)

    float_type = torch.float32 if precision == "single" else torch.float16

    for input_step, (time, model_input) in enumerate(input_data):
        logger.info(f"Starting processing input @ {time}")
        results = retrieval_step(
            model,
            model_input,
            tile_size=tile_size,
            device=device,
            float_type=float_type
        )
        logger.info(f"Finished processing input @ {time}")

        n_retrieved = len(results) - forecast

        drop_left = temporal_overlap // 2
        for step in range(n_retrieved):

            curr_time = time - (n_retrieved - step - 1) * input_data.time_step

            results_s = results[step]
            results_s["time"] = curr_time.astype("datetime64[ns]")
            date = to_datetime(curr_time)
            date_str = date.strftime("%Y%m%d_%H_%M")
            output_file = output_path / f"chimp_{date_str}.nc"

            if input_step > 0 and output_file.exists() and step < drop_left:
                continue

            results_s.attrs["sequence_step"] = step + 1
            logger.info(f"Writing retrieval results to {output_file}")
            results_s.to_netcdf(output_path / f"chimp_{date_str}.nc")

    return 0
