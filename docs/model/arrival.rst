.. _arrival_model:

Arrival Model
=============

The arrival testing regime of a strategy is comprised of two rounds of testing:
*pre-departure* and *arrival* testing. Pre-departure testing is done before an
individual returns to the central location. If they test positive, they stay
at their current location and are responsible for their own isolation. Upon
receiving a negative pre-departure test, the individual travels to the central
location where they take an arrival test. If they are positive, isolation
must be provided for them.

Given an arrival testing regime, the percent of the population that were
discovered in pre-departure testing and the percent of the population that were
discovered in arrival testing can be computed based on test sensitivities and
compliance. These discoverd people may be infected or recovered people that
were hidden.

The simulation is initialized with both those discovered in pre-departure
testing and arrival testing as discovered and recovered. The recovered
population that was hidden and the infected population not discovered through
the arrival process stays hidden in recovered and infected respectively.

In reporting metrics when an arrival period is being considered, the results of
the simulation are tapered for the duration of the arrival period. This
tapering assumes the the population returns at a constant rate through the
arrival period. The simulation results are independent of the arrival
period as the simulation code only supports a constant population. Hence,
metrics are pessimistic in the sense that the simulation begins with the full
level of internal interaction amongst the population even though the population
hasn't fully arrived. The effects of this can be counteracted by supplying
transmission multipliers to the :py:mod:`simpar.strategy.Strategy` class.
