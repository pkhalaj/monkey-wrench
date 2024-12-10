Introduction
-------------

**Monkey wrench** gathers the tools to run pre-trained Neural Network (NN)
models for precipitation intensity using satellite data, based on the `CHIMP`_
framework, fetch and process its input files, analyse and visualise its output,
and much more! It is an attempt to avoid *reinventing the wheel* by
consolidating all Python scripts and codes that we use at SMHI alongside CHIMP.
While the Chalmers/CSU Integrated Multi-Satellite Retrieval Platform, CHIMP, is
rather a general framework for training, evaluating and running NN based
retrievals of physical properties from remote-sensing observations, the focus
of this utility package has so far been NN based retrievals of precipitation
intensity using satellite data, and CHIMP will be used here synonymously with
such already pre-trained models.

In particular, with *Monkey wrench* you can:

* Query and fetch SEVIRI data from the EUMETSAT API via either single queries or batches
* Resample fetched files from the API
* Use the provided CHIMP extensions to allow for reading files which are not natively supported by CHIMP
* Perform queries on local files, datetime objects, and conversion between filenames and datetime stamps
* Run CHIMP for different groups of input files in a queue
* Perform post-processing of CHIMP output as well as some visualization utilities
* Use it as a task runner

*Monkey wrench* has been developed at the Swedish Meteorological and
Hydrological Institute (SMHI_) as part of the *Skyfall* project, partly funded
by the Swedish Civil Contingencies Agency (MSB_).
  
.. note::
    Monkey Wrench uses the `eumdac`_ package for API calls.
    This allows for customized downloading of files from EUMETSAT Data Store tailored to our needs. However, our wrapper
    does not utilize or even expose all the functionalities of the ``eumdac``, at least not yet!

.. _CHIMP: https://github.com/simonpf/chimp
.. _eumdac: https://gitlab.eumetsat.int/eumetlab/data-services/eumdac
.. _SMHI: https://www.smhi.se
.. _MSB: https://www.msb.se
