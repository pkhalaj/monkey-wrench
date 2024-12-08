Use mode
========

You can use Monkey Wrench in two modes:

* As a python package which can be easily imported and used in python codes/scripts.

* As a standalone executable, essentially serving as a task manager which reads and runs task from YAML files.

For examples on how to use Monkey Wrench, refer to `examples`_. Therein you can find several example sub-directories.
In each sub-directory, there are two files, namely ``script.py`` and ``task.yaml``. The former demonstrates how
Monkey Wrench can be used as a Python package, and the other shows how you can use Monkey Wrench as a task runner.

Note that the two modes are equivalent and the results are identical. As a result, depending on your use case, you can
choose a use mode that you deem fit.


Package mode
------------

As an example, to obtain all product IDs for SEVIRI native data between ``2015/06/01`` (inclusive) and ``2015/08/01``
(exclusive) and save them in :file:`seviri_product_ids.txt`, you can do the following in a Python script

.. code-block:: python

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


The above example is available in `script.py`_.

Task runner mode
----------------

One can achieve the same results as the `Package mode`_, but using the task runner instead. Create a new YAML file
with the following content and an arbitrary valid filename, e.g. ``task.yaml``

.. code-block:: yaml

    context: ids
    action: fetch
    specifications:
        start_datetime: [2015, 6, 1]
        end_datetime: [2015, 8, 1]
        batch_interval:
            days: 30
        output_filename: seviri_product_ids.txt


Then run the task via

.. code-block:: bash

    monkey-wrench task.yaml


The above example is available in `task.yaml`_. The results are identical to those of the `Package mode`_ example.


.. _examples: https://github.com/pkhalaj/monkey-wrench/tree/main/examples
.. _script.py: https://github.com/pkhalaj/monkey-wrench/blob/main/examples/fetch_product_ids/script.py
.. _task.yaml: https://github.com/pkhalaj/monkey-wrench/blob/main/examples/fetch_product_ids/task.yaml
