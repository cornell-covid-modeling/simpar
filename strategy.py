import numpy as np
from testing_regime import TestingRegime
from typing import List

class Strategy:

    def __init__(self,
        name: str,
        pct_discovered_in_pre_departure: float,
        pct_discovered_in_arrival_test: float,
        testing_regimes: List[TestingRegime],
        transmission_multipliers: List[float],
        period_lengths: List[int]):
        """Initialize a strategy for Spring 2022 Covid-19 response.

        Args:
            name (str): Name for this strategy.
            pct_discovered_in_pre_departure (float): Percentage of active \
                positives who are discovered as a result of pre-departure testing.
            pct_discovered_in_arrival_test (float): Percentage of active \
                positives who are discovered as a result of arrival testing.
            testing_regimes (List[TestingRegime]): Testing regime to be used in \
                each period of the simulation.
            transmission_multipliers (List[float]): Transmission multiplier to \
                be used in each period of the simulation.
            period_lengths (List[int]): Length (in generations) of each period \
                of the simulation.
        """
        self.name = name
        self.pct_discovered_in_pre_departure = pct_discovered_in_pre_departure
        self.pct_discovered_in_arrival_test = pct_discovered_in_arrival_test

        n = len(period_lengths)
        assert len(testing_regimes) == n
        assert len(transmission_multipliers) == n

        self.periods = n
        self.testing_regimes = testing_regimes
        self.transmission_multipliers = transmission_multipliers
        self.period_lengths = period_lengths

    def get_initial_and_past_infections(self, params):
        """Return the initial and past infections vectors used to init sim.

        Args:
            params (Dict): Parameters for the simultion
        """
        dec_surge_infections = np.array(params["dec_surge_infections"])
        winter_break_infections = np.array(params["winter_break_infections"])
        active_infections = np.array(params["active_infections"])

        pct_discovered = self.pct_discovered_in_pre_departure + \
                         self.pct_discovered_in_arrival_test
        # all of these past infections begin as recovered in the simulation
        # TODO (hwr26): Maybe it makes more sense to initialize the sim with
        # the people found in arrival testing as discovered infectious
        past_infections = dec_surge_infections + \
                          winter_break_infections + \
                          (pct_discovered * active_infections)
        initial_infections = (1 - pct_discovered) * active_infections
        return past_infections, initial_infections
