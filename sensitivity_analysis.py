import yaml
import json
import numpy as np
from groups import population
import metrics
from transform import transform
from scenario import ScenarioFamily
from sim_helper import sim_test_strategy
from sp22_strategies import sp22_no_testing_strategy, sp22_1x_week_testing_strategy
import plotting

COLORS = ['#084594', '#2171b5', '#4292c6', '#6baed6',
          '#9ecae1', '#c6dbef', '#deebf7', '#f7fbff']

# =======================
# [Initialize Parameters]
# =======================

nominal = yaml.safe_load(open("nominal.yaml", "r"))
nominal["meta_matrix"] = \
    np.array([list(row.values()) for row in nominal["meta_matrix"].values()])
# load prior
scenario_family = ScenarioFamily(nominal, yaml.safe_load(open("prior.yaml", "r")))

# ==========================
# [Run] Compare trajectories
# ==========================

no_testing_trajectories = []
once_week_trajectories = []
for _ in range(100):
    scenario = scenario_family.get_sampled_scenario()
    no_testing_traj = \
        sim_test_strategy(scenario=scenario,
                          strategy=sp22_no_testing_strategy(scenario),
                          color="#9ecae1",
                          name=str(scenario["booster_rate"]["FS"]))
    once_testing_traj = \
        sim_test_strategy(scenario=scenario,
                          strategy=sp22_1x_week_testing_strategy(scenario),
                          color="#800080",
                          name=str(scenario["booster_rate"]["FS"]))
    no_testing_trajectories.append(no_testing_traj)
    once_week_trajectories.append(once_testing_traj)

# ======
# [Plot]
# ======

plotting.plot_comprehensive_confidence_interval_summary(
    outfile="sensitivity_analysis.png",
    trajectories=[no_testing_trajectories, once_week_trajectories]
)
