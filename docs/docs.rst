.. _docs:

Documentation
=============

The core implementation of the SIR model is maintained in the
:py:mod:`simpar.sim` module (details of this model can be found in the
:ref:`model` section). It contains the :py:mod:`simpar.sim.Sim` class
which is initialized with simulation parameters. The
:py:func:`simpar.sim.Sim.step` method steps the simulation forward in time.

The :py:mod:`simpar.micro` module defines a single function called
:py:mod:`simpar.micro.days_infectious` which returns the given number of days
someone is expected to be free and infectious given the number of days between
surveillance tests, the delay in receiving test results (isolation delay), the
sensitivity of the test, and the maximum number of days someone is infectious.
Details of this computation can be found in the documentation of this module.

The :py:mod:`simpar.groups` module defines the
:py:mod:`simpar.groups.MetaGroup` class which represents a meta-group as
defined in the :ref:`population_model` section. It can be initialized from a
dictionary. The :py:mod:`simpar.groups.Population` class is comprised of a set
of meta-groups along with a meta-group contact matrix describing how these
meta-groups interact with one another. This can also be initialized from a
dictionary. It is responsible for managing the indices of the groups
associated with each meta-group. Given S, R, D, and H counts at the meta-group
level, The :py:mod:`simpar.groups.Population.get_init_SIR_and_DH` returns
the initial counts at the group level. Furthermore, the class offers methods to
return the infection matrix, outside rate, and both the infection and
discovered recovery fractions.

The :py:mod:`simpar.strategy` module defines a pandemic response strategy.
This is comprised of an isolation regime, arrival testing regime, and
testing regime (used once the population has arrived). Each has its own
respective class. Both testing regimes maintain lists of the
:py:mod:`simpar.strategy.Test` class which maintains the properties of a test.
This can be initialized from a dictionary allowing for representation in a
parameter file such as JSON or YAML.

The :py:mod:`simpar.scenario` module defines the
:py:mod:`simpar.scenario.Scenario` class which maintains all of the parameters
pertaining to a scenario under which a disease is spreading. This consists of a
:py:mod:`simpar.groups.Population` alongside environment parameters
(e.g. outside rate of infection) and disease parameters (e.g. symptomatic
rate). This can be initialized from a dictionary allowing for representation in
a parameter file such as JSON or YAML. Furthermore, it offers the
:py:mod:`simpar.scenario.Scenario.simulate_strategy` method which returns a
completed simulation run under a given strategy.

Lastly, the :py:mod:`simpar.trajectory` module defines the
:py:mod:`simpar.trajectory.Trajectory` class which is comprised of a
simulation and scenario and strategy on which it was run. This class offers
multiple methods for returning key metrics of the simulation.


.. toctree::
   :maxdepth: 2

   simpar
