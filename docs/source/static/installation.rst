Prerequisites and installation
===============================

Miniforge
---------
The hard requirement of using Monkey Wrench is being able to make a ``conda`` environment. As a result, install
`mamba <https://github.com/mamba-org/mamba>`_ via the `Miniforge <https://github.com/conda-forge/miniforge>`_
GitHub.

Installation of CHIMP and Monkey Wrench
_______________________________________

1- Clone the repository

.. code-block:: bash

    git clone https://github.com/pkhalaj/monkey-wrench.git


2- All the requirements for running CHIMP is in :doc:`chimp.yaml <../../../envs/chimp.yaml>`.
The file provides a conda environment with the same name (excluding the ``.yaml`` extension). To install and activate
the available conda environment, run:

.. code-block:: bash

    mamba env create -f monkey-wrench/envs/chimp.yaml
    mamba activate chimp


3- install the package via

.. code-block:: bash

    pip install monkey-wrench

To install dependencies for development (e.g. tests and documentation)

.. code-block::

    pip install -e "monkey-wrench[dev]"


CHIMP models
------------

To run a CHIMP retrieval, you also need to download a retrieval model. You can automatically get the latest version of
the model from `Hugging Face <https://huggingface.co/>`_ using `git-lfs <https://git-lfs.com/>`_. It is a dependency
defined in :doc:`chimp.yaml <../../../envs/chimp.yaml>` and has been installed in the conda
environment you just created.

However, you need to update Git hooks (once per user account), via
.. code-block::

    git lfs install

Now you can fetch the latest model and store it in a directory, e.g. ``chimp_retrieval_models``
.. code-block::

    git clone https://huggingface.co/simonpf/chimp_smhi chimp_retrieval_models

You can also inspect and download the models manually from

* versions before ``v3``: `<https://rain.atmos.colostate.edu/gprof_nn/chimp/>`_
* version ``v3`` and later: `<https://huggingface.co/simonpf/chimp_smhi>`_

See :ref:`CHIMP models and results<CHIMP models and results>`, if you need to know more about the models.

API credentials
-------------------

1- Visit `API key management <https://api.eumetsat.int/api-key/>`_ to obtain credentials to access the EUMETSAT API.

2- Set environment variables for API credentials so that they can be picked up by ``monkey-wrench`` via
.. code-block::

    export EUMETSAT_API_LOGIN=<login>
    export EUMETSAT_API_PASSWORD=<password>

You need to replace ``<login>`` and ``<password>`` with your actual credentials and this needs to be done in every new
shell instance.
