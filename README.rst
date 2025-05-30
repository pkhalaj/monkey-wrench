**Monkey Wrench** provides tools to run `CHIMP`_, fetch and process its input files, analyze and visualize its
output, and much more! It is an attempt to avoid *reinventing the wheel* by consolidating all Python scripts and
codes that we use alongside CHIMP.

In particular, you can:

- |checked| Querying and fetching SEVIRI data from the EUMETSAT API via either single queries or batches
- |checked| Resampling fetched files from the API
- |checked| Using the provided CHIMP extensions to allow for reading files which are not natively supported by CHIMP
- |checked| Performing queries on local files, datetime objects, and conversion between filenames and datetime stamps
- |checked| Running CHIMP for different groups of input files in a queue
- |checked| Running tasks from YAML files, alleviating the need for coding
- |unchecked| Performing post-processing of CHIMP output as well as some visualization utilities

N.B. **Monkey Wrench** is a work in progress and under active development. As a result, the API and the scheme of task (YAML) files might and will change!

**License, Disclaimer of Warranty, and Limitation of Liability**

  This program is distributed under the `GNU General Public License Version 3`_.  You should have received a copy of the GNU General Public License along with this program. If not, see `<https://www.gnu.org/licenses/gpl-3.0.html>`_.

.. _CHIMP: https://github.com/simonpf/chimp
.. _GNU General Public License Version 3: https://www.gnu.org/licenses/gpl-3.0.html
.. |checked| unicode:: U+2611
.. |unchecked| unicode:: U+2610
