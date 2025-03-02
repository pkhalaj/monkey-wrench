Prerequisites and installation
==============================

Miniforge
---------
Using Monkey Wrench requires a working ``conda`` environment. One can install `mamba`_
through `Miniforge`_.

Installation of CHIMP and Monkey Wrench
---------------------------------------

1. Clone the repository

.. code-block:: bash

    git clone https://github.com/pkhalaj/monkey-wrench.git


2. All the requirements for running CHIMP are in `chimp.yaml`_. The file provides a conda environment with the same
   name (excluding the :samp:`.yaml` extension). To install and activate the available conda environment, run:

.. code-block:: bash

    mamba env create -f monkey-wrench/envs/chimp.yaml
    mamba activate chimp


3. Install the package via:

.. code-block:: bash

    pip install monkey-wrench


To install dependencies for development (e.g., tests and documentation):

.. code-block:: bash

    pip install -e "monkey-wrench[dev]"


CHIMP models
------------

To run a CHIMP retrieval, you also need to download a retrieval model. You can automatically get the latest version of
the model from `Hugging Face`_ using `git-lfs`_. It is a dependency defined in `chimp.yaml`_ and has been installed
in the conda environment you just created.

However, you need to update Git hooks (once per user account), via

.. code-block:: bash

    git lfs install


Now you can fetch the latest model and store it in a directory, e.g. :file:`./chimp_retrieval_models/`

.. code-block:: bash

    git clone https://huggingface.co/simonpf/chimp_smhi chimp_retrieval_models

You can also inspect and download the models manually from

* versions before ``v3``: `<https://rain.atmos.colostate.edu/gprof_nn/chimp/>`_
* version ``v3`` and later: `<https://huggingface.co/simonpf/chimp_smhi>`_

See :doc:`CHIMP models and results <chimp_models>`, if you need to know more about the models.

API credentials
---------------

1. Visit `API key management`_ to obtain credentials to access the EUMETSAT API.

2. Set environment variables for API credentials so that they can be picked up by Monkey Wrench:

.. code-block:: bash

    export EUMETSAT_API_LOGIN=<login>
    export EUMETSAT_API_PASSWORD=<password>

You need to replace ``<login>`` and ``<password>`` with your actual credentials. Note that this needs to be done in every new
shell instance unless added to your shell profile.


.. _API key management: https://api.eumetsat.int/api-key
.. _Hugging Face: https://huggingface.co
.. _Miniforge: https://github.com/conda-forge/miniforge
.. _chimp.yaml: https://github.com/pkhalaj/monkey-wrench/blob/main/envs/chimp.yaml
.. _git-lfs: https://git-lfs.com
.. _mamba: https://github.com/mamba-org/mamba
