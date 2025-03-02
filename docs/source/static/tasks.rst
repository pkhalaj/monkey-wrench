Tasks
=====

.. role:: iyaml(code)
   :language: yaml

The following are specifications and examples of different keys and values in ``task.yaml`` files, depending on
different scenarios. The YAML files are parsed and first validated by `Pydantic`_ and any errors are logged.

Every task is a `YAML`_ document which consists of the following parts, or the so-called nodes:

* ``context``: literal string
* ``action``: literal string
* ``specifications``: mapping

The ``context`` determines the general category of the task. For example, :iyaml:`context: ids` means we are dealing
with a task related to product IDs. The ``action`` is a verb which describes what needs to be done. For example in the
context of ids, :iyaml:`action: fetch` means product IDs need to be fetched from the EUMETSAT Datastore. Finally,
``specifications`` is a dictionary which gives details of the action, such as ``start_datetime``.

.. note::
    It is possible to have several tasks in the same file. Since each task is a YAML document, tasks can be separated by
    three dashes ``---``.

The following is the content of a task file which obtains all product IDs for SEVIRI native data between ``2015/06/01``
(inclusive) and ``2015/08/01`` (exclusive) and saves them in :file:`seviri_product_ids.txt`

.. code-block:: yaml

    context: ids
    action: fetch
    specifications:
      start_datetime: "2015-06-01T00:00:00+00:00"
      end_datetime: "2015-08-01T00:00:00+00:00"
      batch_interval:
        days: 30
      output_filepath: seviri_product_ids.txt

Specifications depend on the context and the action as explained below.

Examples
--------

Product IDs
+++++++++++

Fetch SEVIRI product IDs

.. code-block:: yaml

    context: ids
    action: fetch
    specifications:
      batch_interval: <required>
      end_datetime: <required>
      output_filepath: <required>
      start_datetime: <required>

Files
+++++

Download and resample SEVIRI native files

.. code-block:: yaml

    context: files
    action: fetch
    specifications:
      area: <required>
      end_datetime: <required>
      input_filepath: <required>
      parent_output_directory_path: <required>
      start_datetime: <required>

      channel_names: <optional>
      dataset_save_options: <optional>
      fsspec_cache: <optional>
      number_of_processes: <optional>
      output_filename_generator: <optional>
      radius_of_influence: <optional>
      remove_file_if_exists: <optional>
      temp_directory_path: <optional>

Verify that files exist according to the expected product IDs, given datetime range, and the patterns

.. code-block:: yaml

    context: files
    action: verify
    specifications:
      end_datetime: <required>
      nominal_file_size: <required>
      parent_input_directory_path: <required>
      reference: <required>
      start_datetime: <required>

      file_size_relative_tolerance: <optional>
      number_of_processes: <optional>
      pattern: <optional>
      verbose: <optional>

CHIMP Retrieval
+++++++++++++++

Process SEVIRI files with CHIMP model to retrieve cloud parameters

.. code-block:: yaml

    context: chimp
    action: retrieve
    specifications:
      end_datetime: <required>
      model_filepath: <required>
      parent_input_directory_path: <required>
      parent_output_directory_path: <required>
      start_datetime: <required>

      device: <optional>
      sequence_length: <optional>
      temporal_overlap: <optional>
      temp_directory_path: <optional>
      tile_size: <optional>
      verbose: <optional>

Specifications
--------------

Datetime instances
++++++++++++++++++

.. code-block:: yaml

    Keys:
      start_datetime
      end_datetime

    Description:
      String indicating the datetime in ISO format with timezone information.

    Python type:
      datetime.datetime

    Supported in:
      ids:
        fetch
      files:
        fetch
        verify
      chimp:
        retrieve

Example

.. code-block:: yaml

    start_datetime: "2022-08-12T00:00:00+00:00"


Datetime intervals
++++++++++++++++++

.. code-block:: yaml

    Keys:
      batch_interval

    Description:
      Dictionary indicating the interval for each batch when fetching product IDs.

    Values:
      dictionary:
        keys:
          weeks
          days
          hours
          minutes
          seconds
        values:
          non-negative integers

    Python type:
      datetime.timedelta

    Supported in:
      ids:
        fetch

Example:

.. code-block:: yaml

    batch_interval:
        days: 30
        hours: 10


Paths
+++++

.. code-block:: yaml

    Keys:
      input_filepath                # must point to an existing file
      output_filepath               # must be a new path as overwriting an existing file is not allowed!
      reference                     # must point to an existing file containing reference product IDs
      parent_input_directory_path   # must point to an existing directory
      parent_output_directory_path  # must point to an existing directory
      temp_directory_path           # must point to an existing directory for temporary files
      model_filepath                # must point to an existing model file

    Description:
      A string which can be interpreted as a valid path. It can point to either relative or absolute paths.
      Internally, it will be parsed into an absolute path for consistency.

    Python type:
      pathlib.Path

    Supported in:
      ids:
        fetch:
          output_filepath
      files:
        fetch:
          input_filepath
          parent_output_directory_path
          temp_directory_path
        verify:
          reference
          parent_input_directory_path
      chimp:
        retrieve:
          model_filepath
          parent_output_directory_path
          parent_input_directory_path
          temp_directory_path

Example

.. code-block:: yaml

    input_filepath: products_ids.txt
    parent_output_directory_path: /path/to/output/directory
    reference: /path/to/product_ids.txt


Pattern
+++++++

.. code-block:: yaml

    Keys:
      pattern

    Description:
      A dictionary containing the pattern to filter filenames.

    Values:
      sub_strings:
        A single literal string or a list of literal strings used to filter filenames. This is optional,
        and if absent from the task file, no filtering will be performed on the filenames.
        The pattern does not support wildcards or regex, only literals.
      case_sensitive:
        A boolean indicating whether the pattern should be case-sensitive or not.
      match_all:
        A boolean indicating whether all or any of the sub_strings should be present in the filename.

    Default:
      pattern: null
      case_sensitive: true
      match_all: true

    Python type:
      sub_strings: str | list[str] | None
      case_sensitive: bool
      match_all: bool

    Supported in:
      files:
        verify


.. code-block:: yaml

    pattern:
      sub_strings:
        - "seviri"
        - "nc"
      case_sensitive: false
      match_all: false

Numbers
+++++++

.. code-block:: yaml

    Keys:
      number_of_processes
      nominal_file_size               # in bytes
      file_size_relative_tolerance
      radius_of_influence
      sequence_length
      temporal_overlap
      tile_size

    Description:
      Positive integers for counts and sizes, float values for tolerance parameters.

    Default:
      number_of_processes: 1
      file_size_relative_tolerance: 0.01
      radius_of_influence: 20000
      sequence_length: 16
      temporal_overlap: 0
      tile_size: 256

    Python type:
      int | float

    Supported in:
      files:
        fetch:
          number_of_processes
          radius_of_influence
        verify:
          number_of_processes
          nominal_file_size
          file_size_relative_tolerance
      chimp:
        retrieve:
          sequence_length
          temporal_overlap
          tile_size


Device Selection
++++++++++++++++

.. code-block:: yaml

    Keys:
      device

    Description:
      String indicating computation device to use.

    Values:
      Literal["cpu", "cuda"]

    Default:
      "cpu"

    Python type:
      str

    Supported in:
      chimp:
        retrieve


Verbose Options
+++++++++++++++

.. code-block:: yaml

    Keys:
      verbose

    Description:
      Boolean indicating whether to enable verbose output
      or a list of string options specifying which verbose information to show.

    Values:
      true | false | list[Literal["files", "reference", "corrupted", "missing"]]

    Default:
      false

    Python type:
      bool | list[Literal["files", "reference", "corrupted", "missing"]]

    Supported in:
      files:
        verify
      chimp:
        retrieve

Examples

.. code-block:: yaml

    verbose: true

or

.. code-block:: yaml

    verbose:
      - corrupted
      - missing


Function References
+++++++++++++++++++

.. code-block:: yaml

    Keys:
      output_filename_generator

    Description:
      String containing the fully qualified function path of Monkey Wrench excluding the leading `monkey_wrench.`

    Default:
      input_output.seviri.input_filename_from_product_id

    Python type:
      str

    Supported in:
      files:
        fetch



Cache Options
+++++++++++++

.. code-block:: yaml

    Keys:
      fsspec_cache

    Description:
      String indicating the cache type to use with fsspec.

    Values:
      Literal["filecache", "blockcache"] | null

    Default:
      null

    Python type:
      str | None

    Supported in:
      files:
        fetch

Example

.. code-block:: yaml

    fsspec_cache: filecache


Channel Configuration
+++++++++++++++++++++

.. code-block:: yaml

    Keys:
      channel_names

    Description:
      List of strings representing channel names to process.

    Default:
      - "VIS006"
      - "VIS008"
      - "IR_016"
      - "IR_039"
      - "WV_062"
      - "WV_073"
      - "IR_087"
      - "IR_097"
      - "IR_108"
      - "IR_120"
      - "IR_134"
      - "HRV"

    Python type:
      list[str]

    Supported in:
      files:
        fetch


Dataset Save Options
++++++++++++++++++++

.. code-block:: yaml

    Keys:
      dataset_save_options

    Description:
      Dictionary with configuration options for saving datasets.

    Default:
      writer: "cf"            # "cf" for "netcdf", i.e. the format for writing the data
      include_lonlats: false

    Python type:
      dict

    Supported in:
      files:
        fetch


Area Definitions
++++++++++++++++

.. code-block:: yaml

    Keys:
      area

    Description:
      Dictionary with area definitions conforming to the `Pyresample` package.

    Python type:
      dict

    Supported in:
      files:
        fetch

Example

.. code-block:: yaml

    area:
      CHIMP_NORDIC_4:
        description: "CHIMP region of interest over the nordic countries"
        projection:
          proj: "stere"
          lat_0: 90
          lat_ts: 60
          lon_0: 14
          x_0: 0
          y_0: 0
          datum: "WGS84"
          no_defs: null
          type: "crs"
        shape:
          height: 564
          width: 452
        area_extent:
          lower_left_xy: [-745322.8983833211, -3996217.269197446]
          upper_right_xy: [1062901.0232376591, -1747948.2287755085]
          units: "m"


Remove File Options
+++++++++++++++++++

.. code-block:: yaml

    Keys:
      remove_file_if_exists

    Description:
      Boolean indicating whether to remove existing files before processing.

    Default:
      true

    Python type:
      bool

    Supported in:
      files:
        fetch

.. _Pydantic: https://docs.pydantic.dev/latest
.. _YAML: https://yaml.org/spec/1.2.2
