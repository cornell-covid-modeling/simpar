import yaml
import numpy as np
import pandas as pd
from scenario import ScenarioFamily
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
    scenario_family = ScenarioFamily(nominal, yaml.safe_load(open("prior.yaml", "r")))

    # generate N random trajectories sampled from the prior
    np.random.seed(0)
    trajectories = []
    for _ in range(100):
        scenario = scenario_family.get_sampled_scenario()
        traj = sim_test_strategy(scenario=scenario,
                                strategy=sp22_no_testing_strategy(scenario),
                                color="white")
        trajectories.append(traj)

    # initialize groups to create projections for
    groups = {
        "Total": None,
        "Students": ["UG_on", "UG_off", "GR_on", "GR_off", "PR_on", "PR_off"],
        "Staff": ["FS"]
    }

    # create CSV with projected discovered with confidence intervals
    df = pd.DataFrame()
    scenario = trajectories[0].scenario
    df['x'] = np.arange(scenario["T"]) * scenario["generation_time"]

    for group in groups:
        metric = lambda x: get_total_discovered(x, metagroup_names=groups[group])
        lb, nominal, ub = confidence_interval(trajectories, metric)
        df[f"{group}_05"] = lb
        df[f"{group}_50"] = nominal
        df[f"{group}_95"] = ub
    df.to_csv("sp22_projections.csv")


if __name__ == "__main__":
    main()
