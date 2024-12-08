CHIMP models and results
========================

Models
------

``chimp_smhi_v0``
+++++++++++++++++

- ResNeXt architecture with ``5M`` parameters
- Trained on 1-year of collocations
- Scene size ``128``


``chimp_smhi_v1``
+++++++++++++++++

- EfficientNet-V2 architecture with ``20M`` parameters
- Trained on 1-year of collocations
- Scene size ``256``

.. note::
    The ``chimp_smhi_v1``  models should be run with a tile size of ``256``.


``chimp_smhi_v2``
+++++++++++++++++

- EfficientNet-V2 2p1 architecture with ``~40M`` parameters
- Trained on 2-year of collocations over Europe and the Nordics
- Scene size ``256``

.. note::
    The ``chimp_smhi_v2``  models should be run with a tile size of ``256`` and a sequence length of ``16``.


``chimp_smhi_v3``
+++++++++++++++++

There are two ``chimp_smhi`` version 3 models. The ``chimp_smhi_v3`` model processes single inputs, while the
``chimp_smhi_v3_seq`` model processes multiple inputs.

.. note::
    | The ``chimp_smhi_v3``  model should be run with a tile size of ``256``.
    | The ``chimp_smhi_v3_seq``  model should be run with a tile size of ``256`` and a sequence length of ``16``.


Results
--------

The results are written as ``NetCDF4`` datasets to the provided output directory.
Currently the only retrieved variable is ``dbz_mean``. Since CHIMP retrievals are probabilistic, the ``_mean``
suffix is added to the variable name highlight that it is the expected value of the retrieved posterior distribution.
