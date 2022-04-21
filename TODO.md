# TODO

## Offered Functionality

Support for this situation:
- A population returns to an institution
- The population is heterogeneous with different contact levels
- Some of the population has already been infected
- An arrival testing procedure (pre-departure + arrival testing) is used
- A testing procedure is in effect once people are back
- Rate of outside infection + infection spreading within population

Should have a standard dictionary (called scenario) that can be
constructed from a dictionary coming out of amps (or YAML/JSON parser
directly). This eliminates dependency on amps or a parser. Examples would
use parser and maybe amps as well.

## Module Breakdown

### sim module
- Given initialization and necessary parameters (minimal--they should be
  computed from other modules), this module should run the core of the
  simulation for a heterogeneous population.
- Largely, this code will be accessed by scaffolding that manages the map from
  contact levels within metagroups to individual groups in the simulation
- How should computing metrics be encoded? Separate module on top?
  Troublesome metric of computing isolation which requires isolation strategy

### groups module
- Provide function to compute initial and infection_matrix
- Requires user to facilitate interaction between `sim` and `groups`--is that
  wanted (more flexibility / less coupling) or not (less required of user)
- Direct access to population but not metagroups?
- Initialize a population from scenario dictionary

### isolation module
- This should be moved into some metric-responsible module

### micro module
- Computes how long someone is expected to be infectious given a certain
  scenario and testing strategy
- Need to understand this module a little bit better

### strategy module
- Contains needed ArrivalTestingRegime and TestingRegime classes
- The Strategy class is a collection of the two regimes
- Need to factor out Cornell-specific parameters like winter break

### sim_helper + trajectory + plotting module
- Wrapper bringing things together
- Offer plotting functionality
- Should plotting be part of the package? Probably
- -> Should be able to use without plotting though too

### metrics module
- Compute complicated metrics from Trajectory objects
- Should compute metrics from completed simulation directly
- Easily be able to add metrics (remove complex Cornell-specific metrics)

## Module Architecture

```
---------
|  sim  |      core simulation (flat notion of groups)
---------
    |
  sim returns (simple metrics) used in ??? metric computations
    |
    |               ----------
    | <-----------  | groups |   metagroups privatized and population is public
    |               ----------   population initialized from standard dictionary
    |
-----------
|   ???   |   sim wrapper (notion of metagroups with contact levels)
-----------
    |
   ??? returns metagroup-level metrics



------------
| strategy |    maintains classes to encode
------------    - pre-departure + arrival testing regime
                - testing regime
                - strategy (some pair of above--maybe changing over time)

TODO: Think through this further
```