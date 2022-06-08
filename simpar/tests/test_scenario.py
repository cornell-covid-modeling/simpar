import os
import yaml
from simpar.scenario import Scenario
from simpar.strategy import strategies_from_dictionary


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')
with open(os.path.join(RESOURCES_PATH, "test_scenario.yaml"), "r") as f:
    yaml_file = yaml.safe_load(f)
    SCENARIO = Scenario.from_dictionary(yaml_file)
    STRATEGY = strategies_from_dictionary(yaml_file, SCENARIO.tests)["test"]


def test_simulate_strategy():
    """Test simulate_strategy method of Scenario class."""
    SCENARIO.simulate_strategy(STRATEGY)
