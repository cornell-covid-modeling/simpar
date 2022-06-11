|brand_image|
=============

|

simpar (SIMulate PAndemic Response) simulates the spread of a disease through a
heterogeneous population using an `SIR model`_. The :py:mod:`simpar.groups`
module can be used to manage a heterogeneous population comprised of
"meta-groups" with varying contact levels. The tool focuses on providing
functionality for assessing pandemic response strategies such as isolation
protocols, testing regimes (with varying tests), and vaccination requirements.
The :py:class:`simpar.strategy.Strategy` class is used to define a potential
strategy. The :py:class:`simpar.scenario.Scenario` class is used to manage the
parameters pertaining to a scenario under which a disease is spreading. This
consists of a population, environment parameters (e.g. outside rate of
infection), and disease parameters (e.g. symptomatic rate). Lastly, the
:py:class:`simpar.trajectory.Trajectory` class offers methods to compute
metrics on a simulation of some strategy applied to a scenario.

To install simpar, see :ref:`install`. For a detailed description of the model
used to simulate disease spread, see :ref:`model`. It is recommended for both
users and those interested in developing to read this section. Lastly, for an
overview of the package structure and the complete documentation, see
:ref:`docs`.


.. _SIR model: https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology
.. |brand_image| image:: branding/simpar_color.png
  :height: 100
  :alt: simpar

.. toctree::
   :maxdepth: 2

   install
   model/index
   docs
