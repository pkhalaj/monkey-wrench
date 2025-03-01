Introduction
-------------

**Monkey Wrench** gathers the tools to run pre-trained neural network (NN) models for
precipitation intensity using satellite data, based on the **Chalmers/CSU Integrated
Multi-Satellite Precipitation Retrieval Program**, also referred to as `CHIMP`_ for short.
CHIMP, is a general framework for training, evaluating and running NN based retrievals of physical
properties from remote-sensing observations. However, the focus of **Monkey Wrench**
has so far been NN based retrievals of precipitation intensity using satellite data,
and CHIMP will be used here synonymously with such already pre-trained models.

In particular, **Monkey Wrench** includes utilities to fetch and process CHIMP input files,
analyze and visualize its output, and much more! It is an attempt to avoid
*reinventing the wheel* by consolidating all Python scripts and codes that we use
at `SMHI`_ alongside CHIMP.

Example use cases of **Monkey wrench**:

* Querying and fetching SEVIRI data from the EUMETSAT API via either single queries or batches
* Resampling fetched files from the API
* Using the provided CHIMP extensions to allow for reading files which are not natively supported by CHIMP
* Perform queries on local files, datetime objects, and conversion between filenames and datetime stamps
* Running CHIMP for different groups of input files in a queue
* Performing post-processing of CHIMP output as well as some visualization utilities
* Running tasks from YAML files, alleviating the need for coding

.. note::
  **Monkey Wrench** has been developed at the Swedish Meteorological and
  Hydrological Institute (SMHI_) as part of the *Skyfall* project, partly funded
  by the Swedish Civil Contingencies Agency (MSB_).

.. note::
  **Monkey Wrench** uses the `eumdac`_ package for API calls.
  This allows for customized downloading of files from EUMETSAT Data Store tailored to our needs. However, our wrapper
  does not utilize or even expose all the functionalities of the ``eumdac``, at least not yet!

.. warning::
  **Monkey Wrench** is a work in progress and under active development. As a result, the API and the scheme of task (YAML) files might and will change!

**License, Disclaimer of Warranty, and Limitation of Liability**

  This program is distributed under the `GNU General Public License Version 3`_. You should have received a copy of the GNU General Public License along with this program. If not, see `<https://www.gnu.org/licenses/gpl-3.0.html>`_.

.. _CHIMP: https://github.com/simonpf/chimp
.. _GNU General Public License Version 3: https://www.gnu.org/licenses/gpl-3.0.html
.. _eumdac: https://gitlab.eumetsat.int/eumetlab/data-services/eumdac
.. _SMHI: https://www.smhi.se
.. _MSB: https://www.msb.se
