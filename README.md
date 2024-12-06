# Introduction

**Monkey wrench** gathers the tools to run [CHIMP](https://github.com/simonpf/chimp), fetch and process its input files,
analyse and visualise its output, and much more! It is an attempt to avoid _reinventing the wheel_ by consolidating all
Python scripts and codes that we use alongside CHIMP.

In particular, you can:

- Query and fetch SEVIRI data from the EUMETSAT API, via
    - single queries: fast and convenient
    - batches: suitable for cases that you get the `too many requests` error from the EUMETSAT API.
- Resample fetched files from the API
- Use the provided CHIMP extensions to allow for reading files which are not natively supported by CHIMP
- Perform queries on local files and/or datetime objects as well as conversion between filenames and their corresponding
  datetime stamps.
- Run CHIMP for different groups of input files in a queue.
- Perform post-processing of CHIMP output as well as some visualization utilities.
- Use it as a task runner.

> EUMETSAT API: We wrap around the [eumdac](https://gitlab.eumetsat.int/eumetlab/data-services/eumdac) package to allow
> for customized downloading of files from EUMETSAT Data Store. Our wrapper does not expose all the functionalities of
> the `eumdac`, only the few ones that we need!

----

# Prerequisites and Installation

## Miniforge

Install [mamba](https://github.com/mamba-org/mamba) via the [Miniforge](https://github.com/conda-forge/miniforge)
GitHub.

## Installation of CHIMP and Monkey Wrench

1. Clone the repository

``` shellsession
git clone https://github.com/pkhalaj/monkey-wrench.git
```

2. All the requirements for running CHIMP is in [chimp.yaml](./envs/chimp.yaml). The file provides a conda environment
   with the same name (excluding the `.yaml` extension). To install and activate the available conda environment, run:

``` shellsession
mamba env create -f monkey-wrench/envs/chimp.yaml
mamba activate chimp
```

3. Assuming that the cloned repository is inside the `monkey-wrench` directory, install the package via

```python
pip install monkey-wrench
```

This will install the package as well as any other dependencies.

To install dependencies for development (e.g. tests and documentation)

```python
pip install -e "monkey-wrench[dev]"
```

## Chimp models

To run a CHIMP retrieval, you also need to download a retrieval model. You can automatically get the latest version of
the model from [Hugging Face](https://huggingface.co/) using [git-lfs](https://git-lfs.com/). It is a dependency defined in
[chimp.yaml](./envs/chimp.yaml) and has been installed in the conda environment you just created.
However, you need to update Git hooks (once per user account), via
```commandline
git lfs install
```
Now you can fetch the latest model and store it in a directory, e.g. `chimp_retrieval_models`
```commandline
git clone https://huggingface.co/simonpf/chimp_smhi chimp_retrieval_models
```
You can also inspect and download the models manually from
- versions
`<  v3`: [https://rain.atmos.colostate.edu/gprof_nn/chimp/](https://rain.atmos.colostate.edu/gprof_nn/chimp/).
- versions `>= v3`: [https://huggingface.co/simonpf/chimp_smhi](https://huggingface.co/simonpf/chimp_smhi).

See [CHIMP models and results](#CHIMP-models-and-results), if you need to know more about the models.

## API credentials

1. Visit [API key management](https://api.eumetsat.int/api-key/) to obtain credentials to access the EUMETSAT API.

2. Set environment variables for API credentials so that they can be picked up by `monkey-wrench` via
```commandline
export EUMETSAT_API_LOGIN=<login>
export EUMETSAT_API_PASSWORD=<password>
```
You need to replace `<login>` and `<password>` with your actual credentials and this needs to be done in every new
shell instance.

----

# Use mode

You can use `monkey-wrench` in two modes:

- As a python package which can be easily imported and used in python codes/scripts.
- As a standalone executable, essentially serving as a task manager which reads and runs task from `.yaml` files.

For examples on how to use Monkey Wrench, refer to [examples](./examples). Therein you can find several example
sub-directories. In each sub-directory, there are two files, namely `script.py` and `task.yaml`. The former demonstrates
how Monkey Wrench can be used as a Python package, and the other shows how you can use Monkey Wrench as a task runner.
Note that the two modes are equivalent and the results are identical. As a result, depending on your use case, you can
choose a use mode that you deem fit.

## Package mode

As an example, to obtain all product IDs for SEVIRI native data between `2015/06/01` (inclusive) and `2015/08/01`
(exclusive) and save them in `seviri_product_ids.txt`, you can do the following in a Python script

```python
from datetime import datetime, timedelta
from pathlib import Path

from monkey_wrench.io_utils import write_items_to_txt_file_in_batches
from monkey_wrench.query_utils import EumetsatAPI, EumetsatCollection

filename = Path("seviri_product_ids.txt")

api = EumetsatAPI(
    collection=EumetsatCollection.seviri,
    log_context="Example [Fetch Product IDs]"
)

product_batches = api.query_in_batches(
    start_datetime=datetime(2015, 6, 1),
    end_datetime=datetime(2015, 8, 1),
    batch_interval=timedelta(days=30)
)

write_items_to_txt_file_in_batches(product_batches, filename)
```
The above example is available in [example/fetch_product_ids/script.py](./examples/fetch_product_ids/script.py).

## Task runner mode
One can achieve the same results as the [package mode](#package-mode), but using the task runner instead. Create a
new `.yaml` file with the following content and an arbitrary valid filename, e.g. `task.yaml`
```yaml
context: ids
action: fetch
specifications:
  start_datetime: [2015, 6, 1]
  end_datetime: [2015, 8, 1]
  batch_interval:
    days: 30
  output_filename: ./seviri_product_ids.txt
```
Then run the task via
```commandline
monkey-wrench task.yaml
```
The above example is available in [examples/fetch_product_ids/task.yaml](./examples/fetch_product_ids/task.yaml). The
results are identical to those of the [package mode](#package-mode) example. Refer to [examples/README.md](./examples/README.md)
for more information.

----

# CHIMP models and results

## Models

### ``chimp_smhi_v0``

- ResNeXt architecture with 5M parameters
- Trained on 1-year of collocations
- Scene size 128

### ``chimp_smhi_v1``

- EfficientNet-V2 architecture with 20M parameters
- Trained on 1-year of collocations
- Scene size 256

> **NOTE:** The ``chimp_smhi_v1``  models should be run with a tile size of 256.

### ``chimp_smhi_v2``

- EfficientNet-V2 2p1 architecture with ~40M parameters
- Trained on 2-year of collocations over Europe and the Nordics
- Scene size 256

> **NOTE:** The ``chimp_smhi_v2``  models should be run with a tile size of 256 and
> a sequence length of 16.

### ``chimp_smhi_v3``

There are two ``chimp_smhi`` version 3 models. The ``chimp_smhi_v3`` model processes single inputs, while the
``chimp_smhi_v3_seq`` model processes multiple inputs.

> **NOTE:** The ``chimp_smhi_v3``  model should be run with a tile size of 256.

> **NOTE:** The ``chimp_smhi_v3_seq``  model should be run with a tile size of 256 and a sequence length of 16.

## Results

The results are written as `NetCDF4` datasets to the provided output directory.
Currently the only retrieved variable is ``dbz_mean``. Since ``chimp`` retrievals are probabilistic, the ``_mean``
suffix is added to the variable name highlight that it is the expected value of the retrieved posterior distribution.
