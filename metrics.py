from functools import reduce
from operator import iconcat
import numpy as np
from trajectory import Trajectory
from isolation import compute_isolated
from typing import List


def get_isolated(trajectory: Trajectory, metagroup_names: List[str] = None):
    """Return the number of isolated individuals at each generation.

    Args:
        trajectory (Trajectory): Trajectory object.
        metagroup_names (List[str]): Limit to isolated in these metagroups.

    Returns:
        np.ndarray: Number of isolated individuals at each generation.
    """
    sim = trajectory.sim
    scenario = trajectory.scenario
    if metagroup_names is None:
        metagroup_names = trajectory.pop.metagroup_names()

    group_idx = trajectory.pop.metagroup_indices(metagroup_names)
    idx = reduce(iconcat, group_idx, [])
    all_metagroup_names = trajectory.pop.metagroup_names()
    metagroup_idx = [all_metagroup_names.index(i) for i in metagroup_names]
    isolated = sim.get_isolated(group=idx,
                                iso_lengths=scenario["isolation_durations"],
                                iso_props=scenario["isolation_fracs"])

    # uniformly spread arrival discovered across three generations
    arrival_discovered_sum = \
        sum(trajectory.strategy.get_arrival_discovered(scenario)[metagroup_idx])
    arrival_discovered = np.zeros(sim.max_T)
    for i in range(scenario["arrival_period"]):
        arrival_discovered[i] += arrival_discovered_sum / scenario["arrival_period"]
    additional_isolated = compute_isolated(discovered=arrival_discovered,
                                           generation_time=sim.generation_time,
                                           iso_lengths=scenario["isolation_durations"],
                                           iso_props=scenario["isolation_fracs"])

    return isolated + additional_isolated


def get_ug_on_isolated(trajectory: Trajectory):
    """Return the isolations among on-campus UGs."""
    return get_isolated(trajectory, metagroup_names=["UG_on"])


def get_ug_pr_isolated(trajectory: Trajectory):
    """Return the isolations among UGs and PRs"""
    metagroup_names = ["UG_on", "UG_off", "PR_on", "PR_off"]
    return get_isolated(trajectory, metagroup_names=metagroup_names)


def get_total_discovered(trajectory: Trajectory, metagroup_names: List[str] = None):
    """Return the number of discovered positives at each generation,
        including those discovered upon arrival.

    Args:
        trajectory (Trajectory): Trajectory object.
        metagroup_names (List[str]): Limit to discovered in these metagroups.

    Returns:
        np.ndarray: Number of discovered individuals at each generation.
    """
    sim = trajectory.sim
    scenario = trajectory.scenario
    if metagroup_names is None:
        metagroup_names = trajectory.pop.metagroup_names()

    group_idx = trajectory.pop.metagroup_indices(metagroup_names)
    idx = reduce(iconcat, group_idx, [])
    all_metagroup_names = trajectory.pop.metagroup_names()
    metagroup_idx = [all_metagroup_names.index(i) for i in metagroup_names]
    discovered = sim.get_total_discovered_for_different_groups(idx, cumulative=True)

    arrival_discovered_sum = \
        sum(trajectory.strategy.get_arrival_discovered(scenario)[metagroup_idx])
    arrival_discovered = np.zeros(sim.max_T)
    for i in range(scenario["arrival_period"]):
        arrival_discovered[i] += arrival_discovered_sum / scenario["arrival_period"]

    return np.cumsum(arrival_discovered) + discovered

def get_total_infected(trajectory: Trajectory, metagroup_names: List[str] = None):
    """Return the number of infected positives at each generation,
        including those discovered to be infected upon arrival.

    Args:
        trajectory (Trajectory): Trajectory object.
        metagroup_names (List[str]): Limit to infected in these metagroups.

    Returns:
        np.ndarray: Number of infected individuals at each generation.
    """
    sim = trajectory.sim
    scenario = trajectory.scenario
    if metagroup_names is None:
        metagroup_names = trajectory.pop.metagroup_names()

    group_idx = trajectory.pop.metagroup_indices(metagroup_names)
    idx = reduce(iconcat, group_idx, [])
    all_metagroup_names = trajectory.pop.metagroup_names()
    metagroup_idx = [all_metagroup_names.index(i) for i in metagroup_names]
    infected = sim.get_total_infected_for_different_groups(idx, cumulative=True)

    arrival_discovered_sum = \
        sum(trajectory.strategy.get_arrival_discovered(scenario)[metagroup_idx])
    arrival_discovered = np.zeros(sim.max_T)
    for i in range(scenario["arrival_period"]):
        arrival_discovered[i] += arrival_discovered_sum / scenario["arrival_period"]

    return np.cumsum(arrival_discovered) + infected

def get_peak_hotel_rooms(trajectory: Trajectory):
    """Return the peak number of hotel room used over the semester."""
    isolated = get_ug_on_isolated(trajectory=trajectory)
    return int(np.ceil(np.max(isolated)))


def get_total_hotel_rooms(trajectory: Trajectory):
    """Return the total number of hotel rooms used over the semester."""
    isolated = get_ug_on_isolated(trajectory=trajectory)
    scenario = trajectory.scenario
    return int(np.ceil(np.sum(isolated) * scenario["generation_time"]))


def get_ug_prof_days_in_isolation_in_person(trajectory: Trajectory):
    """Return the number of undergrad and professional days in isolation
    during the portion of the semester that is in-person."""
    isolated = get_ug_pr_isolated(trajectory=trajectory)
    # TODO (hwr26): Is there some way to compute this from trajectory.strategy?
    START_OF_IN_PERSON = 5 # generation when we start in-person instruction
    scenario = trajectory.scenario
    return int(np.sum(isolated[START_OF_IN_PERSON:]) * scenario["generation_time"])


def get_ug_prof_days_in_isolation(trajectory: Trajectory):
    """Return the number of undergrad and professional days in isolation."""
    isolated = get_ug_pr_isolated(trajectory=trajectory)
    return int(np.sum(isolated) * trajectory.scenario["generation_time"])


def _get_cumulative_hospitalizations(trajectory: Trajectory, metagroups: List[str]):
    """Return the cumulative number of hospitalizations at each generation."""
    s = trajectory.sim
    pop = trajectory.pop
    cumulative_hospitalizations = np.zeros(s.max_T)
    group_idx = pop.metagroup_indices(metagroups)
    for i in range(len(metagroups)):
        cumulative_hospitalizations += \
            s.get_total_infected_for_different_groups(group_idx[i], cumulative=True) * \
            trajectory.scenario["hospitalization_rates"][metagroups[i]] * \
            trajectory.scenario["booster_hospitalization_multiplier"]
    return cumulative_hospitalizations


def get_cumulative_all_hospitalizations(trajectory: Trajectory):
    """Return the cumulative number of all hospitalizations at each generation."""
    pop = trajectory.pop
    metagroups = pop.metagroup_names()
    cumulative_hospitalizations = \
        _get_cumulative_hospitalizations(trajectory, metagroups)
    return cumulative_hospitalizations


def get_total_hospitalizations(trajectory: Trajectory):
    """Return the total number of hospitalizations over the semester."""
    pop = trajectory.pop
    metagroups = pop.metagroup_names()
    cumulative_hospitalizations = \
        _get_cumulative_hospitalizations(trajectory, metagroups)
    return cumulative_hospitalizations[-1]


def get_total_employee_hospitalizations(trajectory: Trajectory):
    """Return the total number of employee hospitalizations over the semester."""
    cumulative_hospitalizations = \
        _get_cumulative_hospitalizations(trajectory, ["FS"])
    return cumulative_hospitalizations[-1]


def get_cumulative_infections(trajectory: Trajectory):
    infected = trajectory.sim.get_infected(aggregate=True, cumulative=True)
    return int(np.ceil(infected[-1]))
