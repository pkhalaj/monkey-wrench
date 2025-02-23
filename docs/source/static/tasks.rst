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
with a task related to product IDs. The ``action`` is a verb which describe what needs to be done. For example in the
context of ids, :iyaml:`action: fetch` means product IDs need to fetched from the EUMETSAT Datastore. Finally,
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
      start_datetime: [2015, 6, 1]
      end_datetime: [2015, 8, 1]
      batch_interval:
        days: 30
      output_filename: seviri_product_ids.txt

Specifications depend on the context and the action as explained below.

Examples
----------

Product IDs
+++++++++++

Fetch SEVIRI product IDs

.. code-block:: yaml

    context: ids
    action: fetch
    specifications:
      start_datetime: <required>
      end_datetime: <required>
      batch_interval: <required>
      output_filename: <required>

Files
+++++

Download and resample SEVIRI native files

.. code-block:: yaml

    context: files
    action: fetch
    specifications:
      start_datetime: <required>
      end_datetime: <required>
      input_filename: <required>
      directory: <required>
      number_of_processes: <required>

Verify that files exist according to the expected product IDs, given datetime range, and the patterns

.. code-block:: yaml

    context: files
    action: verify
    specifications:
      start_datetime: <required>
      end_datetime: <required>
      input_filename: <required>
      directory: <required>
      patterns: <optional>


Specifications
--------------

Datetime instances
++++++++++++++++++

.. code-block:: yaml

    Keys:
      start_datetime
      end_datetime

    Values:
      list:
        min-length: 3
        max-length: 6
        elements: non-negative or positive integers conforming to datetime constraints, e.g. 1 <= month <= 12.

    Python type:
      datetime.datetime

    Required in:
      ids:
        fetch
      files:
        fetch
        verify

Example

.. code-block:: yaml

    start_datetime: [2022, 8, 12]


Datetime intervals
++++++++++++++++++

.. code-block:: yaml

    Keys:
      batch_interval

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

    Required in:
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
      input_directory   # must point to an existing directory
      output_directory  # must point to an existing directory
      input_filename    # must point to an existing file
      output_filename   # must be a new path as overwriting an existing file is not allowed!

    Values:
      a string which can be interpreted as a valid path. It can point to either relative or absolute paths. Internally,
      it will be parsed into an absolute for consistency.

    Python type:
      pathlib.Path

    Required in:
      ids:
        fetch:
          output_filename
      files:
        fetch:
          input_filename
          output_directory
        verify:
          input_filename
          input_directory

Example

.. code-block:: yaml

    input_filename: products_ids.txt



Pattern
+++++++

.. code-block:: yaml

    Keys:
      pattern

    Values:
      A single literal string or a list of literal strings using which filenames are filtered. This is optional and if
      is absent from the task file, means no filtering will be performed on the filenames. The pattern does not support
      wildcard or regex, only literals. In case of a list, all strings must exist in a filename, i.e. patterns are ANDed!

    Python type:
      str | list[str] | None

    Supported in:
      files:
        verify

Examples

.. code-block:: yaml

    pattern: nc

.. code-block:: yaml

    pattern: [seviri, 2022]


Numbers
+++++++

.. code-block:: yaml

    Keys:
      number_of_processes

    Values:
      positive integers, where 1 essentially disables multiprocessing.

    Python type:
      int

    Required in:
      files:
        fetch

Example

.. code-block:: yaml

    number_of_processes: 20


.. _Pydantic: https://docs.pydantic.dev/latest
.. _YAML: https://yaml.org/spec/1.2.2
