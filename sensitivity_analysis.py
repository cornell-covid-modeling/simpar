import yaml
import json
import numpy as np
from groups import population
import metrics
from transform import transform
from scenario import ScenarioFamily
from sim_helper import sim_test_strategy
from sp22_strategies import sp22_testing_strategy
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

trajectories = []
# scalers = np.linspace(0.0,1.0,50)
for _ in range(100):
    scenario = scenario_family.get_sampled_scenario()
    traj = sim_test_strategy(scenario=scenario,
                             strategy=sp22_testing_strategy(scenario),
                             color="white",
                             name=str(scenario["booster_rate"]["FS"]))
    trajectories.append(traj)

# ======
# [Plot]
# ======

plotting.plot_metric_confidence_interval_over_time(
    outfile="sensitivity_analysis.png",
    trajectories=trajectories,
    metric_name="Cumulative Hospitalizations",
    metric=metrics.get_cumulative_all_hospitalizations
)
