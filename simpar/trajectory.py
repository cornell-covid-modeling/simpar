"""Simulation trajectory manager.

Defines a [Trajectory] class which is comprised of a fully run [Sim] that
was the result of applying a given [Strategy] to a [Scenario]. The class
offers methods to return various metrics.
"""

__author__ = "Henry Robbins (henryrobbins)"


import numpy as np
from typing import List
from .scenario import Scenario
from .strategy import IsolationRegime, Strategy
from .sim import Sim


class Trajectory:
    """
    Manages all of the attributes of a simulation run.

    This includes the underlying simulation [Sim] and the scenario [Scenario]
    and the strategy [Strategy] that was used. It also maintains a color and
    name for use when plotting trajectories.
    """

    def __init__(self, scenario: Scenario, strategy: Strategy, sim: Sim,
                 color: str = "black", name: str = None):
        """Initialize a [Trajectory] instance.

        Args:
            scenario (Scenario): Scenario that the simulation was run under.
            strategy (Strategy): Strategy that was used to run the simulation.
            sim (sim): Simulation which used the provided strategy.
            color (str): Color of the trajectory when plotting.
            name (str): Name of the trajectory when plotting.
        """
        self.scenario = scenario
        self.strategy = strategy
        self.sim = sim
        self.color = color
        self.name = strategy.name if name is None else name

    def get_bucket(self, bucket: str, meta_groups: List[str] = None,
                   aggregate: bool = True, cumulative: bool = False,
                   normalize: bool = False):
        """Return the given bucket vector.

        Args:
            bucket (str): One of the simulation buckets: {S, I, R, D, H}.
            meta_groups (List[str]): Meta-groups to aggregate over. \
                Default to all.
            aggregate (bool): Aggregate over the meta-groups if True.
            cumulative (bool): Return cumulative metric over time if True.
            normalize (bool): Normalize relative to total population.
        """
        sim = self.sim
        population = self.scenario.population
        A = {
            "S": sim.S,
            "I": sim.I,
            "R": sim.R,
            "D": sim.D,
            "H": sim.H
        }[bucket]

        # adjust for arrival period
        arrival_period = self.scenario.arrival_period
        if arrival_period is not None:
            for i in range(arrival_period):
                A[i] *= (i / arrival_period)

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

    def get_hospitalizations(self, meta_groups: List[str] = None,
                             aggregate: bool = True, cumulative: bool = False,
                             normalize: bool = False):
        """Return hospitalizations as computed from hospitalization rates.

        Args:
            meta_groups (List[str]): Meta-groups to aggregate over. \
                Default to all.
            aggregate (bool): Aggregate over the meta-groups if True.
            cumulative (bool): Return cumulative metric over time if True.
            normalize (bool): Normalize relative to total population.
        """
        scenario = self.scenario
        population = self.scenario.population

        I = self.get_bucket(bucket="I", meta_groups=meta_groups,
                            aggregate=False, cumulative=cumulative,
                            normalize=normalize)

        if meta_groups is None:
            hospitalization_rates = scenario.hospitalization_rates
        else:
            hospitalization_rates = []
            for i, meta_group in enumerate(population.meta_group_names):
                if meta_group in meta_groups:
                    tmp = scenario.hospitalization_rates[i]
                    hospitalization_rates.append(tmp)

        hospitalizations = hospitalization_rates * I
        if aggregate:
            hospitalizations = np.sum(hospitalizations, axis=1)

        return hospitalizations

    def get_isolated(self, meta_groups: List[str] = None,
                     aggregate: bool = True, cumulative: bool = False,
                     normalize: bool = False):
        """Return the number of isolated individuals at each generation.

        Args:
            meta_groups (List[str]): Limit to isolated in these metagroups.
            aggregate (bool): Aggregate over the meta-groups if True.
            cumulative (bool): Return cumulative metric over time if True.
            normalize (bool): Normalize relative to total population.
        """
        scenario = self.scenario
        generation_time = scenario.generation_time
        isolation_regime = self.strategy.isolation_regime

        D = self.get_bucket(bucket="D", meta_groups=meta_groups,
                            aggregate=aggregate, cumulative=cumulative,
                            normalize=normalize)

        return _get_isolated(D, generation_time, isolation_regime)


def _get_isolated(discovered: np.ndarray, generation_time: float,
                  isolation_regime: IsolationRegime):
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
        isolation_regime (IsolationRegime): Isolation regime being used.
    """
    iso_lengths = isolation_regime.iso_lengths
    iso_props = isolation_regime.iso_props

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
            if t-i > 0:
                tmp = isolation_frac[i] * (discovered[t-i] - discovered[t-i-1])
                isolated[t] = isolated[t] + tmp
            if t-i == 0:
                isolated[t] = isolated[t] + isolation_frac[i] * discovered[t-i]

    return isolated
