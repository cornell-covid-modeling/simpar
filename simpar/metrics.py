"""Trajectory metrics manager.

Contains all metric methods which take a Trajectory as input.
"""

__author__ = "Henry Robbins (henryrobbins)"


import numpy as np
from .trajectory import Trajectory
from typing import List


def get_bucket(trajectory: Trajectory, bucket: str,
               meta_groups: List[str] = None, aggregate: bool = True,
               cumulative: bool = False, normalize: bool = False):
    """Return the given bucket vector.

    Args:
        trajectory (Trajectory): Trajectory to compute metric for,.
        bucket (str): One of the simulation buckets: {S, I, R, D, H}.
        meta_groups (List[str]): Meta-groups to aggregate over. Default to all.
        aggregate (bool): Aggregate over the meta-groups if True.
        cumulative (bool): Return cumulative metric over time if True.
        normalize (bool): Normalize relative to total population.
    """
    sim = trajectory.sim
    population = trajectory.scenario.population
    A = {"S": sim.S, "I": sim.I, "R": sim.R, "D": sim.D, "H": sim.H}[bucket]

    # aggregate across meta-groups
    A_ = []
    if meta_groups is None:
        meta_groups = population.meta_group_names
    for meta_group in meta_groups:
        idx = population.meta_group_ids(meta_group)
        A_.append(np.sum(A[:, idx], axis=1))
    A = np.array(A_).T

    if aggregate:
        x = np.sum(A, axis=1)
    else:
        x = A

    if cumulative:
        x = np.cumsum(x, axis=0)

    if normalize:
        total_pop = np.sum(sim.S + sim.I + sim.R, axis=1)[0]
        x /= total_pop

    return x


def get_hospitalizations(trajectory: Trajectory, meta_groups: List[str] = None,
                         aggregate: bool = True, cumulative: bool = False,
                         normalize: bool = False):
    """Return hospitalizations as computed from hospitalization rates.

    Args:
        trajectory (Trajectory): Trajectory to compute metric for,.
        meta_groups (List[str]): Meta-groups to aggregate over. Default to all.
        aggregate (bool): Aggregate over the meta-groups if True.
        cumulative (bool): Return cumulative metric over time if True.
        normalize (bool): Normalize relative to total population.
    """
    scenario = trajectory.scenario
    population = trajectory.scenario.population

    I = get_bucket(trajectory, bucket="I", meta_groups=meta_groups,
                   aggregate=False, cumulative=cumulative,
                   normalize=normalize)

    if meta_groups is None:
        hospitalization_rates = scenario.hospitalization_rates
    else:
        hospitalization_rates = []
        for i, meta_group in enumerate(population.meta_group_names):
            if meta_group in meta_groups:
                hospitalization_rates.append(scenario.hospitalization_rates[i])

    hospitalizations = hospitalization_rates * I
    if aggregate:
        hospitalizations = np.sum(hospitalizations, axis=1)

    return hospitalizations


def _get_isolated(discovered: np.ndarray, generation_time: float,
                  iso_lengths: List[int], iso_props: List[int]):
    """Return the isolated count (not including the arrival positives).

    As an intermediate step, this function calculates isolation_frac, which
    tells us what fraction of discovered positives need isolation.
    isolation_frac[i] is the fraction of people discovered i generations ago
    that require isolation in the current generation. For example, suppose 80%
    of people require isolation for 2 generations and 20% for only 1. Then
    isolation_frac = [1, .2] is appropriate because all of the people
    discovered in the current generation require isolation and only 20% of
    those discovered in the previous generation still require isolation.

    As another example:
    If 80% of people require isolation for 5 days and 20% for 10 days, then set
    iso_lengths = [5,10] and iso_props = [0.8, 0.2] so that
    isolation_frac[0] = 1,
    isolation_frac[1] = 0.2*1 + 0.8*(5-4)/4 = 0.4
    isolation_frac[2] = 0.2*(10-8)/4 = 0.1

    Args:
        discovered (np.ndarray): Number of people discovered.
        generation_time (float): The number of days per generation.
        iso_lengths (List[int]): List of isolation lengths (in days).
        iso_props (List[int])): List of probability of isolation lengths.
    """
    max_isolation = int(np.ceil(iso_lengths[-1] / generation_time))

    # Compute isolation_frac as described above
    isolation_frac = np.ones(max_isolation)
    for t in range(1,max_isolation):
        isolation_frac[t] = 0
        for i, duration in enumerate(iso_lengths):
            isolation_frac[t] += \
                iso_props[i] * \
                np.clip((duration - generation_time*t) / generation_time, 0, 1)

    isolated = np.zeros(discovered.shape)
    for t in range(len(discovered)):
        for i in range(max_isolation):
            if t-i >= 0:
                isolated[t] = isolated[t] + isolation_frac[i] * discovered[t-i]

    return isolated


def get_total_discovered(trajectory: Trajectory, meta_groups: List[str] = None,
                         aggregate: bool = True, cumulative: bool = False,
                         normalize: bool = False):
    """Return the number of discovered individuals at each iteration.

    This includes those discovered in arrival spread across the arrival period.

    Args:
        trajectory (Trajectory): Trajectory object.
        meta_groups (List[str]): Limit to isolated in these metagroups.
        aggregate (bool): Aggregate over the meta-groups if True.
        cumulative (bool): Return cumulative metric over time if True.
        normalize (bool): Normalize relative to total population.
    """
    D = get_bucket(trajectory, bucket="D", meta_groups=meta_groups,
                   aggregate=aggregate, cumulative=cumulative,
                   normalize=normalize)
    # TODO: think through this--I think this is double counting
    arrival_discovered = _get_arrival_discovered(trajectory, meta_groups,
                                                 aggregate=aggregate,
                                                 normalize=normalize)
    return D + arrival_discovered


def get_total_isolated(trajectory: Trajectory, meta_groups: List[str] = None,
                       aggregate: bool = True, cumulative: bool = False,
                       normalize: bool = False):
    """Return the number of isolated individuals at each generation.

    This includes those isolating as a result of being discovered upon arrival.

    Args:
        trajectory (Trajectory): Trajectory object.
        meta_groups (List[str]): Limit to isolated in these metagroups.
        aggregate (bool): Aggregate over the meta-groups if True.
        cumulative (bool): Return cumulative metric over time if True.
        normalize (bool): Normalize relative to total population.
    """
    scenario = trajectory.scenario

    generation_time = scenario.generation_time
    iso_lengths = scenario.isolation_lengths
    iso_props = scenario.isolation_fracs

    total_discovered = get_total_discovered(trajectory, meta_groups, aggregate,
                                            cumulative, normalize)
    total_isolated = _get_isolated(total_discovered, generation_time,
                                   iso_lengths, iso_props)

    return total_isolated


def _get_arrival_discovered(trajectory: Trajectory,
                            meta_groups: List[str] = None,
                            aggregate: bool = False,
                            cumulative: bool = False,
                            normalize: bool = False):
    """Return arrival discovered (spread across the arrival period)."""
    sim = trajectory.sim
    scenario = trajectory.scenario
    population = scenario.population
    strategy = trajectory.strategy

    # Get total arrival discovered
    arrival_discovered_sum = \
        strategy.get_arrival_discovered(
            scenario.init_recovered, scenario.init_infections,
            scenario.pct_recovered_discovered_arrival)
    if meta_groups is not None:
        names = population.meta_group_names
        idx = [i for i, mg in enumerate(meta_groups) if mg in names]
        arrival_discovered_sum = arrival_discovered_sum[idx]

    # Spread arrival discoverd over the arrival period
    if meta_groups is None:
        K = len(population.meta_group_list)
    else:
        K = len(meta_groups)
    arrival_discovered = np.zeros((sim.max_T, K))
    for i in range(scenario.arrival_period):
        arrival_discovered[i] += \
            arrival_discovered_sum / scenario.arrival_period

    if aggregate:
        x = np.sum(arrival_discovered, axis=1)
    else:
        x = arrival_discovered

    if cumulative:
        x = np.cumsum(x, axis=0)

    if normalize:
        total_pop = np.sum(sim.S + sim.I + sim.R, axis=1)[0]
        x /= total_pop

    return x
