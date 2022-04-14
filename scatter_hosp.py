import yaml
import json
import numpy as np
from groups import population
import metrics
from transform import transform
import amps
from sim_helper import sim_test_strategy
from sp22_strategies import sp22_no_testing_strategy, sp22_1x_week_testing_strategy
import matplotlib.pyplot as plt
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
scenario_family = amps.ScenarioFamily(nominal, yaml.safe_load(open("prior.yaml", "r")))

# ==========================
# [Run] Compare trajectories
# ==========================

no_testing_trajectories = []
once_week_trajectories = []
np.random.seed(0)
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
xs = []
ys = []
for i in range(100):
    xs.append(metrics.get_total_hospitalizations(no_testing_trajectories[i]))
    ys.append(metrics.get_total_hospitalizations(once_week_trajectories[i]))

plt.scatter(xs,ys)
plt.plot(xs, xs, color = 'red', label = 'x=y')
plt.title('Hospitalizations: No student testing vs 1x/week')
plt.xlabel('Hospitalizations with no student testing')
plt.xlabel('Hospitalizations with UG/professional 1x/wk testing')
plt.legend(['One scenario','Dividing line w/ equal hospitalizations'])

plt.savefig('scatter_hosp.png')

