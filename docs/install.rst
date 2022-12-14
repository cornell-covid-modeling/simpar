.. _install:

Installation
============

See the `Quickstart`_ instructions to start using simpar quickly. For those
interested in developing for simpar, see the `Development`_ instructions where
we walk through an editable installation of simpar on a Python virtual
environment and running the test suite and linter.

Quickstart
----------

The quickest way to get started with the simpar package is with pip. Run the
following command to install it.

.. code-block:: bash

   pip install simpar

Development
-----------

We welcome contributions from the community for this project! Here is the
preferred development setup. First, clone the repository.

.. code-block:: bash

   git clone https://github.com/cornell-covid-modeling/simpar

Next, create a Python virtual environment and install simpar with the
:code:`-e` flag and the development dependencies.

.. code-block:: bash

   cd simpar
   python3 -m venv venv
   source venv/bin/activate
   pip install -e ."[dev]"

The included Makefile includes a few targets to help with development:
:code:`test` runs the test suite, :code:`cov` gives a coverage report in the
command line, :code:`cov-html` opens an interactive coverage report in the
browser, and :code:`lint` runs the flake8 linter on the source code to ensure
it follows PEP 8 standards.
