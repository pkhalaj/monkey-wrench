Use mode
========

You can use Monkey Wrench in two modes:

* As a Python package which can be easily imported and used in Python codes/scripts.

* As a standalone executable, essentially serving as a task manager which reads and runs task from YAML files.

For examples on how to use Monkey Wrench, refer to `examples`_. Therein you can find several example sub-directories.
In each sub-directory, there are two files, namely ``script.py`` and ``task.yaml``. The former demonstrates how
Monkey Wrench can be used as a Python package, and the other shows how you can use Monkey Wrench as a task runner.

Note that the two modes are equivalent and the results are identical. As a result, depending on your use case, you can
choose a use mode that you deem fit.


Package mode
------------

As an example, to obtain all product IDs for SEVIRI native data between ``2022/01/01`` (inclusive) and ``2024/01/01``
(exclusive) and save them in :file:`seviri_product_ids.txt`, you can do the following in a Python script

.. code-block:: python

    from datetime import UTC, datetime, timedelta
    from pathlib import Path

    from monkey_wrench.date_time import DateTimeRangeInBatches
    from monkey_wrench.input_output import Writer
    from monkey_wrench.query import EumetsatQuery

    output_filepath = Path("<replace_with_the_full_path_of_the_text_file_in_which_product_ids_are_to_be_stored>")

    writer = Writer(output_filepath=output_filepath)
    datetime_range_in_batches = DateTimeRangeInBatches(
        start_datetime=datetime(2022, 1, 1, tzinfo=UTC),
        end_datetime=datetime(2024, 1, 1, tzinfo=UTC),
        batch_interval=timedelta(days=30)
    )

    if __name__ == "__main__":
        product_batches = EumetsatQuery().query_in_batches(datetime_range_in_batches)
        number_of_items = writer.write_in_batches(product_batches)
        print("number of items successfully fetched and written to the file: ", number_of_items)


The above example is available in `script.py`_.

Task runner mode
----------------

One can achieve the same results as the `Package mode`_, but using the task runner instead. Create a new YAML file
with the following content and an arbitrary valid filename, e.g. ``task.yaml``

.. code-block:: yaml

    context: ids
    action: fetch
    specifications:
    start_datetime: "2022-01-01T00:00:00+00:00"
    end_datetime: "2024-01-01T00:00:00+00:00"
    batch_interval:
        days: 30
    output_filepath: <replace_with_the_full_path_of_the_text_file_in_which_product_ids_are_to_be_stored>


Then run the task via

.. code-block:: bash

    monkey-wrench task.yaml


The above example is available in `task.yaml`_. The results are identical to those of the `Package mode`_ example.


.. _examples: https://github.com/pkhalaj/monkey-wrench/tree/main/examples
.. _script.py: https://github.com/pkhalaj/monkey-wrench/blob/main/examples/fetch_product_ids/script.py
.. _task.yaml: https://github.com/pkhalaj/monkey-wrench/blob/main/examples/fetch_product_ids/task.yaml
