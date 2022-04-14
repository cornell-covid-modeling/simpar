from curses import meta
from cv2 import mean
import yaml
import numpy as np
import pandas as pd
import amps
from sim_helper import sim_test_strategy
from sp22_strategies import sp22_no_testing_strategy
from metrics import get_total_discovered


# TODO (hwr26): Copied code from plotting. Factor similar functionality out.
def confidence_interval(trajectories, metric):
    """Add confidence interval of [metric] to the axes [ax]."""
    # sort the trajectories
    ys = [metric(trajectory) for trajectory in trajectories]
    ys = sorted(ys, key=lambda x: x[-1])

    # compute the confidence interval
    limit = ((1 - 0.95) / 2)
    lb = ys[int(len(ys) * limit)]
    nominal = ys[int(len(ys) * 0.5)]
    ub = ys[int(len(ys) * (1 - limit))]

    return lb, nominal, ub


def main():
    # initialize scenario family from nominal and prior YAML files
    nominal = yaml.safe_load(open("nominal.yaml", "r"))
    nominal["meta_matrix"] = \
        np.array([list(row.values()) for row in nominal["meta_matrix"].values()])
    scenario_family = amps.ScenarioFamily(nominal, yaml.safe_load(open("prior.yaml", "r")))
    nominal_scenario = scenario_family.get_nominal_scenario()

    # create trajectory
    trajectory = sim_test_strategy(scenario=nominal_scenario,
                                   strategy=sp22_no_testing_strategy(nominal_scenario),
                                   color="white")

    # create CSV with projected discovered
    df = pd.DataFrame()
    df['x'] = np.arange(nominal_scenario["T"]) * nominal_scenario["generation_time"]
    df['y'] = get_total_discovered(trajectory)
    df.to_csv("sp22_projections.csv")


if __name__ == "__main__":
    main()
