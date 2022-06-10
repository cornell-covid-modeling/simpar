.. _model:

Model
=====

The core model that simulates the disease spread is a classic `SIR model`_.
First, we give a brief overview of this model, as used in this implementation,
in :ref:`sir_model`. Although the code is modularized in such a way
that this core implementation can be used directly, the wrapping code assumes
a given population model defined in :ref:`population_model`. Lastly, the
:ref:`arrival_model` section describes how arrival testing is modelled with
respect to the core SIR model.


.. toctree::
   :maxdepth: 1

   sir
   population
   arrival


.. _SIR model: https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology
