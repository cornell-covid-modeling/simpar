"""Scenario for disease spread.

This module defines a [Scenario] class which maintains a scenario on which a
testing strategy can be applied. By combining a scenario with a testing
strategy, a simulation can be run allowing for the comparison of multiple
testing strategies on a single scenario.
"""

__author__ = "Henry Robbins (henryrobbins)"


import numpy as np
from typing import List, Dict
from simpar.sim import Sim
from simpar.groups import Population
from simpar.strategy import Test, Strategy


class Scenario:
    """
    This class maintains a scenario on which a testing strategy can be applied.

    A scenario is a list of parameters which describe the population of people,
    the environment, and the disease spreading. By combining a scenario with a
    testing strategy, a simulation can be run allowing for the comparison of
    multiple testing strategies on a single scenario.
    """

    def __init__(self, population: Population, max_T: int,
                 generation_time: float,
                 infections_per_contact_unit: np.ndarray,
                 init_infections: np.ndarray, init_recovered: np.ndarray,
                 outside_rate: np.ndarray,
                 max_infectious_days: float,
                 symptomatic_rate: float,
                 no_surveillance_test_rate: np.ndarray,
                 pct_recovered_discovered: np.ndarray,
                 hospitalization_rates: np.ndarray,
                 arrival_period: float, tests: Dict[str, Test]):
        """Initialize a [Scenario] instance.

        Args:
            population (Population): The population.
            max_T (int): The length of the simulation.
            generation_time (float): Number of days per generation of sim.
            infections_per_contact_unit (np.ndarray): Number of infections \
                per contact unit across meta-groups.
            init_infections (np.ndarray): Number of initial infections \
                across meta-groups.
            init_recovered (np.ndarray): Number of initial recovered \
                across meta-groups.
            outside_rate (np.ndarray): The number of infections caused by \
                outside infection in a generation time across meta-groups.
            max_infectious_days (float): Maximum period someone is infectious.
            symptomatic_rate (float): Symptomatic rate.
            no_surveillance_test_rate (np.ndarray): Rate at which people test \
                under no surveillance testing across meta-groups.
            pct_recovered_discovered (np.ndarray): Percentage of the \
                recovered population who are discovered across meta-groups.
            hospitalization_rates (np.ndarray): Rate of hospitalizations \
                among those who get infected across meta-groups.
            arrival_period (float): The number of generations the arrival \
                occurs over. Testing is assumed constant over these days. If \
                there is no arrival period, set to None.
            tests (Dict[str, Test]): Dictionary of available tests.
        """
        self.population = population
        self.max_T = max_T
        self.generation_time = generation_time
        self.infections_per_contact_unit = infections_per_contact_unit
        self.init_infections = init_infections
        self.init_recovered = init_recovered
        self.outside_rate = outside_rate
        self.max_infectious_days = max_infectious_days
        self.symptomatic_rate = symptomatic_rate
        self.no_surveillance_test_rate = no_surveillance_test_rate
        self.pct_recovered_discovered = pct_recovered_discovered
        self.hospitalization_rates = hospitalization_rates
        self.arrival_period = arrival_period
        self.tests = tests

    @staticmethod
    def from_dictionary(d: Dict):
        """Initialize a [Scenario] instance from a dictionary."""
        max_T = d["max_T"]
        generation_time = d["generation_time"]
        max_infectious_days = d["max_infectious_days"]
        symptomatic_rate = d["symptomatic_rate"]
        tests = {k: Test.from_dictionary(k, v) for k,v in d["tests"].items()}
        population = Population.from_truncated_paretos_dictionary(d)

        order = d["meta_groups"]
        infect_per_contact_unit = \
            _to_np_array(d["infections_per_contact_unit"], order)
        init_infections = \
            _to_np_array(d["init_infections"], order)
        init_recovered = \
            _to_np_array(d["init_recovered"], order)
        outside_rate = \
            _to_np_array(d["outside_rate"], order)
        no_surveillance_test_rate = \
            _to_np_array(d["no_surveillance_test_rate"], order)
        pct_recovered_discovered = \
            _to_np_array(d["pct_recovered_discovered"], order)
        hospitalization_rates = \
            _to_np_array(d["hospitalization_rates"], order)
        arrival_period = d["arrival_period"]

        return Scenario(population=population, max_T=max_T,
                        generation_time=generation_time,
                        infections_per_contact_unit=infect_per_contact_unit,
                        init_infections=init_infections,
                        init_recovered=init_recovered,
                        outside_rate=outside_rate,
                        max_infectious_days=max_infectious_days,
                        symptomatic_rate=symptomatic_rate,
                        no_surveillance_test_rate=no_surveillance_test_rate,
                        pct_recovered_discovered=pct_recovered_discovered,
                        hospitalization_rates=hospitalization_rates,
                        arrival_period=arrival_period,
                        tests=tests)

    def simulate_strategy(self, strategy: Strategy):
        """Return a simulation of the given strategy on this scenario."""
        assert sum(strategy.period_lengths) == self.max_T
        if self.arrival_period is None:
            assert strategy.arrival_testing_regime is None

        population = self.population

        # Get initial infections and recovered based on arrival testing
        # Additionally, compute those that are discovered and hidden
        init_infections = strategy.get_initial_infections(self.init_infections)
        init_recovered = strategy.get_initial_recovered(self.init_recovered,
                                                        self.init_infections)
        init_discovered = \
            strategy.get_initial_discovered(self.init_recovered,
                                            self.pct_recovered_discovered,
                                            self.init_infections)
        init_hidden = \
            strategy.get_initial_hidden(self.init_recovered,
                                        self.pct_recovered_discovered,
                                        self.init_infections)
        S0, I0, R0, D0, H0 = \
            population.get_init_SIR_and_DH(init_infections, init_recovered,
                                           init_discovered, init_hidden)

        # Iterate through the time periods of the simulation
        for i, period_length in enumerate(strategy.period_lengths):

            testing_regime = strategy.testing_regimes[i]
            infection_matrix = \
                population.infection_matrix(self.infections_per_contact_unit) \
                * strategy.transmission_multipliers[i]
            infection_discovery_frac = \
                population.infection_discovery_frac(
                    testing_regime.get_infection_discovery_frac(
                        self.symptomatic_rate))
            recovered_discovery_frac = \
                population.recovered_discovery_frac(
                    testing_regime.get_recovered_discovery_frac(
                        self.no_surveillance_test_rate))
            outside_rate = \
                population.outside_rate(self.outside_rate) * \
                strategy.transmission_multipliers[i]

            # initialize sim
            if i == 0:
                sim = Sim(max_T=self.max_T, init_susceptible=S0,
                          init_infected=I0, init_recovered=R0,
                          init_discovered=D0, init_hidden=H0,
                          infection_rate=infection_matrix,
                          infection_discovery_frac=infection_discovery_frac,
                          recovered_discovery_frac=infection_discovery_frac,
                          outside_rate=outside_rate)

            # step forward for this period length
            sim.step(period_length, infection_rate=infection_matrix,
                     infection_discovery_frac=infection_discovery_frac,
                     recovered_discovery_frac=recovered_discovery_frac,
                     outside_rate=outside_rate)

        return sim


def _to_np_array(d: Dict, keys: List):
    """Return a NumPy array of [d] values ordered by [keys]."""
    return np.array([d[key] for key in keys])
