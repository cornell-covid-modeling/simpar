import os
import yaml
from simpar.scenario import Scenario
from simpar.strategy import strategies_from_dictionary
from simpar.metrics import (get_bucket, get_hospitalizations,
                            get_total_isolated, get_total_discovered)
from simpar.trajectory import Trajectory


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')
with open(os.path.join(RESOURCES_PATH, "test_scenario.yaml"), "r") as f:
    yaml_file = yaml.safe_load(f)
    SCENARIO = Scenario.from_dictionary(yaml_file)
    STRATEGY = strategies_from_dictionary(yaml_file, SCENARIO.tests)["test"]
    sim = SCENARIO.simulate_strategy(STRATEGY)
    TRAJECTORY = Trajectory(SCENARIO, STRATEGY, sim)


def test_get_bucket():
    get_bucket(TRAJECTORY, "S")
    get_bucket(TRAJECTORY, "I")
    get_bucket(TRAJECTORY, "R")
    get_bucket(TRAJECTORY, "D")
    get_bucket(TRAJECTORY, "H")


def test_get_hospitalizations():
    get_hospitalizations(TRAJECTORY)
    get_hospitalizations(TRAJECTORY, meta_groups=["g1", "g2"])
    get_hospitalizations(TRAJECTORY, meta_groups=["g1", "g2"], aggregate=True)
    get_hospitalizations(TRAJECTORY, cumulative=True)
    get_hospitalizations(TRAJECTORY, normalize=True)


def test_get_total_isolated():
    get_total_isolated(TRAJECTORY)
    get_total_isolated(TRAJECTORY, meta_groups=["g1", "g2"])
    get_total_isolated(TRAJECTORY, meta_groups=["g1", "g2"], aggregate=True)
    get_total_isolated(TRAJECTORY, cumulative=True)
    get_total_isolated(TRAJECTORY, normalize=True)


def test_get_total_discovered():
    get_total_discovered(TRAJECTORY)
    get_total_discovered(TRAJECTORY, meta_groups=["g1", "g2"])
    get_total_discovered(TRAJECTORY, meta_groups=["g1", "g2"], aggregate=True)
    get_total_discovered(TRAJECTORY, cumulative=True)
    get_total_discovered(TRAJECTORY, normalize=True)
