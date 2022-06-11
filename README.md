# <img alt="simpar" src="docs/branding/simpar_color.png" height="90">

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/simpar.svg)](https://pypi.python.org/pypi/simpar/)
[![CircleCI](https://circleci.com/gh/cornell-covid-modeling/simpar/tree/master.svg?style=shield&circle-token=bab4306a454b23a7ba58c30c3a1d0891a5d6e5ac)](https://circleci.com/gh/cornell-covid-modeling/simpar/tree/master)
[![Documentation Status](https://readthedocs.org/projects/simpar/badge/?version=latest)](https://simpar.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/cornell-covid-modeling/simpar/branch/master/graph/badge.svg?token=VKZ6JFQC0P)](https://codecov.io/gh/cornell-covid-modeling/simpar)

simpar (SIMulate PAndemic Response) simulates the spread of a disease through a
heterogeneous population using an [SIR model][1].
The `groups` module can be used to manage a heterogeneous population comprised
of "meta-groups" with varying contact levels. The tool focuses on providing
functionality for assessing pandemic response strategies such as isolation
protocols, testing regimes (with varying tests), and vaccination requirements.
The `Strategy` class is used to define a potential strategy. The `Scenario`
class is used to manage the parameters pertaining to a scenario under which a
disease is spreading. This consists of a population, environment parameters
(e.g. outside rate of infection), and disease parameters (e.g. symptomatic
rate). Lastly, the `Trajectory` class offers methods to compute metrics on a
simulation of some strategy applied to a scenario. For more details,
see the [Documentation][2].

## Installation

The quickest way to get started is with a pip install.

```bash
pip install simpar
```

## Usage

```python
# imports
import yaml
import numpy as np
from simpar.scenario import Scenario
from simpar.strategy import strategies_from_dictionary
from simpar.trajectory import Trajectory
import matplotlib.pyplot as plt

# load scenario and strategy
with open("dev_scenario.yaml", "r") as f:
    yaml_file = yaml.safe_load(f)
    scenario = Scenario.from_dictionary(yaml_file)

with open("dev_strategy.yaml", "r") as f:
    yaml_file = yaml.safe_load(f)
    strategy = strategies_from_dictionary(yaml_file, scenario.tests)["dev"]

# simulate and create trajectory
sim = scenario.simulate_strategy(strategy)
trajectory = Trajectory(scenario, strategy, sim)
```

## License

Licensed under the [MIT License](https://choosealicense.com/licenses/mit/)


[1]: <https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology> "SIR Model"
[2]: <https://simpar.henryrobbins.com> "documentation"
