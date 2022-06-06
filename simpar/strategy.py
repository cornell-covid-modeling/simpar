import numpy as np
from .groups import Population
from .micro import days_infectious
from typing import List, Dict, Union
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)


class ArrivalTestingRegime:

    def __init__(self, scenario: Dict, pre_departure_test_type: Union[float, dict],
        arrival_test_type: Union[float, dict]):
        """Initialize an arrival testing regime.

        Args:
            scenario (Dict): The scenario under which the testing regime is used.
            pre_departure_test_type (Union[float, dict]): The type of test to \
                be used for pre-departure testing.
            arrival_test_type (Union[float, dict]): The type of test to \
                be used for arrival testing.
        """
        popul = Population.from_scenario(scenario)
        K = len(popul.metagroup_names())

        mg_names = popul.metagroup_names()
        for i in range(len(mg_names)):

            if isinstance(pre_departure_test_type, dict):
                _pre_departure_test_type = pre_departure_test_type[mg_names[i]]
            else:
                _pre_departure_test_type = pre_departure_test_type
            if isinstance(arrival_test_type, dict):
                _arrival_test_type = arrival_test_type[mg_names[i]]
            else:
                _arrival_test_type = arrival_test_type

            pre_departure_sensitivity = \
                scenario["tests"][_pre_departure_test_type]["sensitivity"] * \
                scenario["tests"][_pre_departure_test_type]["compliance"]

            arrival_sensitivity = \
                scenario["tests"][_arrival_test_type]["sensitivity"] * \
                scenario["tests"][_arrival_test_type]["compliance"]

            self.pct_discovered_in_pre_departure = \
                np.multiply(np.ones(K), pre_departure_sensitivity)

            self.pct_discovered_in_arrival_test = \
                np.multiply(
                    1 - self.pct_discovered_in_pre_departure,
                    arrival_sensitivity)

    def get_pct_discovered_in_pre_departure(self):
        return self.pct_discovered_in_pre_departure

    def get_pct_discovered_in_arrival_test(self):
        return self.pct_discovered_in_arrival_test


class TestingRegime:

    def __init__(self, scenario: Dict, test_type: Union[float, dict],
        tests_per_week: Union[float, dict]):
        """Initialize a testing regime.

        Args:
            scenario (Dict): The scenario under which the testing regime is used.
            test_type (Union[float, dict]): The type of test to be used.
            tests_per_week (Union[float, dict]): How often tests are collected.
        """
        popul = Population.from_scenario(scenario)

        K = len(popul.metagroup_names()) # number of meta-groups
        self.days_infectious = np.zeros(K)
        self.infection_discovery_frac = np.zeros(K)
        self.recovered_discovery_frac = np.zeros(K)

        # TODO (hwr26): deprecating this temporaroily
        self.name = ""
        # Name the testing regime
        # if tests_per_week == 0: # No surveillance
        #     self.name = "No surveillance"
        # elif np.isscalar(tests_per_week) and np.isscalar(test_delay):
        #     self.name = "%dx/wk, %.1fd delay" % (tests_per_week, test_delay)
        # else:
        #     self.name = ''
        #     for mg in popul.metagroup_names():
        #         if np.isscalar(tests_per_week):
        #             _tests_per_week = tests_per_week
        #         else:
        #             _tests_per_week = tests_per_week[mg]
        #         if np.isscalar(test_delay):
        #             _test_delay = test_delay
        #         else:
        #             _test_delay = test_delay[mg]

        #         if _tests_per_week > 0:
        #             self.name = self.name + 'mg: %dx/wk %.1fd delay ' % (_tests_per_week, _test_delay)
        #         else:
        #             self.name = self.name + 'mg: no surveillance'


        mg_names = popul.metagroup_names()
        for i in range(len(mg_names)):

            # Extract tests per week and test delay from the function arguments for this meta-group
            if isinstance(tests_per_week, dict):
                _tests_per_week = tests_per_week[mg_names[i]]
            else:
                _tests_per_week = tests_per_week
            if isinstance(test_type, dict):
                _test_type = test_type[mg_names[i]]
            else:
                _test_type = test_type

            # Figure out days between tests, infection_discovery_frac, and recovered_discovery frac
            # for this meta-group
            if _tests_per_week == 0:
                _days_between_tests = np.inf
                self.infection_discovery_frac[i] = scenario["symptomatic_rate"]
                self.recovered_discovery_frac[i] = scenario["no_surveillance_test_rate"][mg_names[i]]
            else:
                _days_between_tests = 7 / _tests_per_week
                self.infection_discovery_frac[i] = 1
                self.recovered_discovery_frac[i] = 1

            sensitivity = scenario["tests"][_test_type]["sensitivity"] * \
                          scenario["tests"][_test_type]["compliance"]
            delay = scenario["tests"][_test_type]["test_delay"]

            self.days_infectious[i] = days_infectious(_days_between_tests, delay, \
                                                 sensitivity=sensitivity, \
                                                 max_infectious_days=scenario["max_infectious_days"])

    def get_days_infectious(self):
        return self.days_infectious

    def get_infection_discovery_frac(self):
        return self.infection_discovery_frac

    def get_recovered_discovery_frac(self):
        return self.recovered_discovery_frac

    def get_name(self):
        return self.name



class Strategy:

    def __init__(self,
        name: str,
        arrival_testing_regime: ArrivalTestingRegime,
        testing_regimes: List[TestingRegime],
        transmission_multipliers: List[float],
        period_lengths: List[int]):
        """Initialize a strategy for Spring 2022 Covid-19 response.

        Args:
            name (str): Name for this strategy.
            arrival_testing_regime: Arrival testing regime to be used.
            testing_regimes (List[TestingRegime]): Testing regime to be used in \
                each period of the simulation.
            transmission_multipliers (List[float]): Transmission multiplier to \
                be used in each period of the simulation.
            period_lengths (List[int]): Length (in generations) of each period \
                of the simulation.
        """
        self.name = name

        if arrival_testing_regime is None:
            self.pct_discovered_in_pre_departure = 0
            self.pct_discovered_in_arrival_test = 0
        else:
            self.pct_discovered_in_pre_departure = \
                arrival_testing_regime.get_pct_discovered_in_pre_departure()
            self.pct_discovered_in_arrival_test = \
                arrival_testing_regime.get_pct_discovered_in_arrival_test()

        n = len(period_lengths)
        assert len(testing_regimes) == n
        assert len(transmission_multipliers) == n

        self.periods = n
        self.testing_regimes = testing_regimes
        self.transmission_multipliers = transmission_multipliers
        self.period_lengths = period_lengths

    def get_initial_infections(self, params):
        """Return the initial infections when this strategy is used."""
        active_infections = np.array(list(params["active_infections"].values()))
        pct_discovered = self.pct_discovered_in_pre_departure + \
                         self.pct_discovered_in_arrival_test
        return (1 - pct_discovered) * active_infections

    def get_past_infections(self, params):
        """Return the past infections (recovered) when this strategy is used."""
        dec_surge_infections = np.array(list(params["dec_surge_infections"].values()))
        winter_break_infections = np.array(list(params["winter_break_infections"].values()))
        active_infections = np.array(list(params["active_infections"].values()))
        pct_discovered = self.pct_discovered_in_pre_departure + \
                         self.pct_discovered_in_arrival_test
        # all of these past infections begin as recovered in the simulation
        # TODO (hwr26): Maybe it makes more sense to initialize the sim with
        # the people found in arrival testing as discovered infectious
        past_infections = dec_surge_infections + \
                          winter_break_infections + \
                          (pct_discovered * active_infections)
        return past_infections

    # TODO pf98 hwr26 Would be good to be able to initialize the simulator where people are discovered
    #  and recovered. This corresponds to someone who arrives as positive, is tested and found immediately.

    def get_arrival_discovered(self, params):
        """Return the infections discovered in arrival when this strategy is used.

        Currently, this refers only to those active cases found through arrival
        testing (NOT pre-departure testing).
        """
        active_infections = np.array(list(params["active_infections"].values()))
        active_arrival_discovered = active_infections * self.pct_discovered_in_arrival_test
        inactive_arrival_discovered = \
            np.multiply(np.array(list(params["winter_break_infections"].values())),
                        np.array(list(params['pct_winter_break_infections_discovered_on_arrival'].values())))
        return active_arrival_discovered + inactive_arrival_discovered
