import os
import yaml
from simpar.scenario import Scenario
from simpar.strategy import strategies_from_dictionary
from simpar.trajectory import Trajectory


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')
with open(os.path.join(RESOURCES_PATH, "test_scenario.yaml"), "r") as f:
    yaml_file = yaml.safe_load(f)
    SCENARIO = Scenario.from_dictionary(yaml_file)
    STRATEGY = strategies_from_dictionary(yaml_file, SCENARIO.tests)["test"]
    sim = SCENARIO.simulate_strategy(STRATEGY)
    TRAJECTORY = Trajectory(SCENARIO, STRATEGY, sim)


def test_get_bucket():
    TRAJECTORY.get_bucket("S")
    TRAJECTORY.get_bucket("I")
    TRAJECTORY.get_bucket("R")
    TRAJECTORY.get_bucket("D")
    TRAJECTORY.get_bucket("H")


def test_get_hospitalizations():
    TRAJECTORY.get_hospitalizations()
    TRAJECTORY.get_hospitalizations(meta_groups=["g1", "g2"])
    TRAJECTORY.get_hospitalizations(meta_groups=["g1", "g2"], aggregate=True)
    TRAJECTORY.get_hospitalizations(cumulative=True)
    TRAJECTORY.get_hospitalizations(normalize=True)


def test_get_isolated():
    TRAJECTORY.get_isolated()
    TRAJECTORY.get_isolated(meta_groups=["g1", "g2"])
    TRAJECTORY.get_isolated(meta_groups=["g1", "g2"], aggregate=True)
    TRAJECTORY.get_isolated(cumulative=True)
    TRAJECTORY.get_isolated(normalize=True)
