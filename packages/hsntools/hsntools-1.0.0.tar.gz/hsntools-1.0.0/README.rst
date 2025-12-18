hsntools
========

|ProjectStatus| |Version| |BuildStatus| |Coverage| |License| |PythonVersions|

.. |ProjectStatus| image:: http://www.repostatus.org/badges/latest/active.svg
   :target: https://www.repostatus.org/#active
   :alt: project status

.. |Version| image:: https://img.shields.io/pypi/v/hsntools.svg
   :target: https://pypi.org/project/hsntools/
   :alt: version

.. |BuildStatus| image:: https://github.com/HSNPipeline/hsntools/actions/workflows/build.yml/badge.svg
   :target: https://github.com/HSNPipeline/hsntools/actions/workflows/build.yml
   :alt: build statue

.. |Coverage| image:: https://codecov.io/gh/HSNPipeline/hsntools/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/HSNPipeline/hsntools
   :alt: coverage

.. |License| image:: https://img.shields.io/pypi/l/hsntools.svg
   :target: https://opensource.org/license/mit
   :alt: license

.. |PythonVersions| image:: https://img.shields.io/pypi/pyversions/hsntools.svg
   :target: https://pypi.org/project/hsntools/
   :alt: python versions

``hsntools`` (formerly 'convnwb') is a module for working with the Human Single-Neuron Pipeline (HSNPipeline).

Overview
--------

This module contains general utilities for working with human single-neuron data and projects.

``hsntools`` is designed for use in the Human Single-Neuron pipeline, which provides a guide and
template structure for human single-neuron projects, including working with data files, converting
data to the `NWB <https://www.nwb.org/>`_ format, and managing projects and analyses.

Available sub-modules in `hsntools` include:

- ``io``: includes save and load functions and utilities for working with files raw and converted data files
- ``nsp``: includes functionality that relating to managing recording files from neural signal processors
- ``objects``: includes objects for storing relevant data, for example electrode or task related information
- ``paths``: includes a `Paths` object and utilities for defining and using a consistent path structure
- ``plts``: includes plot functions for examining data through the conversion process
- ``sorting``: includes functionality relating to managing spike sorting
- ``timestamps``: includes utilities for managing timestamps and aligning data streams
- ``utils``: includes general utilities for working with data through the conversion process

Scope
-----

The `hsntools` module is a helper module for implementing functionality needed for the
`Human Single-Neuron Pipeline`. It includes utilities related to managing and organizing relevant files,
including file I/O, functionality for organizing and aligning multiple data streams and converting
data to standardized data files, and utilities for assisting with running analyses across such data
and generating structured reports.

``hsntools`` provides functionality used within the template for the pipeline, including:

- `PrepTEMPLATE <https://github.com/HSNPipeline/PrepTEMPLATE>`_
- `ConvertTEMPLATE <https://github.com/HSNPipeline/ConvertTEMPLATE>`_
- `AnalyzeTEMPLATE <https://github.com/HSNPipeline/AnalyzeTEMPLATE>`_

Note that `hsntools` is not a module for and does not include functionality for spike sorting or single-neuron analyses.
See the `HSNPipeline Overview <https://github.com/HSNPipeline/Overview>`_ for information and guidance on these
processes and related tooling.

Documentation
-------------

Documentation for the ``hsntools`` module is available
`here <https://hsnpipeline.github.io/hsntools/>`_

Documentation for the HSNPipeline more broadly, which uses ``hsntools`` is available on the
`pipeline website <https://hsnpipeline.github.io/>`_

If you have a question about using ``hsntools`` that doesn't seem to be covered by the documentation, feel free to
open an `issue <https://https://github.com/HSNPipeline/hsntools/issues>`_ and ask!

Dependencies
------------

``hsntools`` is written in Python, and requires Python >= 3.7 to run.

It has the following required dependencies:

- `numpy <https://github.com/numpy/numpy>`_
- `pyyaml <https://github.com/yaml/pyyaml>`_

There are also optional dependencies, that offer extra functionality:

- `pynwb <https://github.com/NeurodataWithoutBorders/pynwb>`_ is needed for validating NWB files
- `matplotlib <https://github.com/matplotlib/>`_ is needed for making plots to check conversions
- `scikit-learn <https://github.com/scikit-learn/scikit-learn>`_ is needed to aligning sync pulses
- `pandas <https://github.com/pandas-dev/pandas>`_ is needed for utilities that load dataframes
- `scipy <https://github.com/scipy/scipy>`_ is needed for some load and timestamp related functions
- `h5py <https://github.com/h5py/h5py>`_ is needed for utilities that open HDF5 files
- `neo <https://github.com/NeuralEnsemble/python-neo>`_ is needed for loading & interacting with NSP files
- `mat73 <https://github.com/skjerns/mat7.3>`_ is needed for loading .mat files version >= 7.3
- `pytest <https://github.com/pytest-dev/pytest>`_ is needed to run the test suite locally

Installation
------------

The current release version of `hsntools` is the 1.X.X release series.

See the
`changelog <https://hsnpipeline.github.io/hsntools/changelog>`_
for notes on major version releases.

**Stable Release Version**

To install the latest stable release, you can use pip:

.. code-block:: shell

    $ pip install hsntools

**Development Version**

To get the current development version, first clone this repository:

.. code-block:: shell

    $ git clone https://github.com/hsnpipeline/hsntools

To install this cloned copy, move into the directory you just cloned, and run:

.. code-block:: shell

    $ pip install .

**Editable Version**

To install an editable version, download the development version as above, and run:

.. code-block:: shell

    $ pip install -e .

Contribute
----------

This project welcomes and encourages contributions from the community!

To file bug reports and/or ask questions about this project, please use the
`Github issue tracker <https://github.com/HSNPipeline/hsntools/issues>`_.

When interacting with this project, please follow the
`code of conduct <https://github.com/HSNPipeline/hsntools/blob/main/CODE_OF_CONDUCT.md>`_.
