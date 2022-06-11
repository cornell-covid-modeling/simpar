"""Manage types of surveillance tests and strategies.

This module defines a [Test] class which maintains properties about a specific
surveillance test. Furthermore, it defines an [IsolationRegime],
[ArrivalTestingRegime], and [TestingRegime] which are used to comprise a
[Strategy]. This specifies how long people are isolated, how people are tested
upon arrival, and what testing regime(s) are used after they arrive and for
what periods of time.
"""

__author__ = "Henry Robbins (henryrobbins)"


import numpy as np
from .micro import days_infectious
from typing import List, Dict
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)


class Test:
    __test__ = False  # include so pytest ignores
    """
    This class maintains properties about a surveillance test.

    It computes [true_sensitivity] as [test_sensitivity] * [compliance] to
    represent the true fraction of infections discovered in a single round of
    testing. This assumes compliance rates are equivalent across both
    the susceptible and infected populations.
    """

    def __init__(self, name: str, test_sensitivity: float, test_delay: float,
                 compliance: float = 1):
        """Initialize a test

        Args:
            name (str): Name of the surveillance test.
            test_sensitivity (float): Probability of positive given infectious.
            test_delay (float): Delay in receiving results from test (in days).
            compliance (float, optional): Compliance with test. Defaults to 1.
        """
        self.name = name
        self.true_sensitivity = test_sensitivity * compliance
        self.test_sensitivity = test_sensitivity
        self.compliance = compliance
        self.test_delay = test_delay

    @staticmethod
    def from_dictionary(name, d):
        """Initialize a [Test] from a dictionary"""
        return Test(name, d["sensitivity"], d["test_delay"], d["compliance"])


class IsolationRegime:
    """
    This class maintains properties about an isolation regime.
    """

    def __init__(self, iso_lengths: List[int], iso_props: List[int]):
        """Initialize an isolation regime.

        Args:
            iso_lengths (List[int]): List of isolation lengths (in days).
            iso_props (List[int])): List of probability of isolation lengths.
        """
        self.iso_lengths = iso_lengths
        self.iso_props = iso_props

    @staticmethod
    def from_dictionary(d):
        """Initialize an [IsolationRegime] from a dictionary"""
        return IsolationRegime(d["iso_lengths"], d["iso_props"])


class ArrivalTestingRegime:
    """
    This class maintains an arrival testing regime.

    It offers methods to return the percentage of people that are discovered
    in pre-departure testing and the percentage of people that are discovered
    upon arrival. This allows for planning surrounding potential isolation of
    those who arrive and test positive.
    """

    def __init__(self, pre_departure_test_type: List[Test],
                 arrival_test_type: List[Test]):
        """Initialize an arrival testing regime.

        Args:
            pre_departure_test_type (List[Test]): The type of test to be used \
                for pre-departure testing per meta-group.
            arrival_test_type (List[Test]): The type of test to be used for \
                arrival testing per meta-group.
        """
        self.pre_departure_test_type = pre_departure_test_type
        self.arrival_test_type = arrival_test_type

    @staticmethod
    def from_dictionary(d: Dict, tests: Dict[str, Test]):
        """Initialize a [ArrivalTestingRegime] instance.

        The dictionary [d] should contain two keys: [pre_departure_test_type]
        and [arrival_test_type] which contain list of strings. These are
        interpreted as keys in the [tests] dictionary which provides the
        corresponding [Test] instance.

        Args:
            d (Dict): Dictionary representing the arrival testing regime.
            tests (Dict[str, Test]): Dictionary of [Test] instances.
        """
        pre_departure_test_type = d["pre_departure_test_type"]
        pre_departure_test_type = [tests[i] for i in pre_departure_test_type]
        arrival_test_type = d["arrival_test_type"]
        arrival_test_type = [tests[i] for i in arrival_test_type]
        return ArrivalTestingRegime(pre_departure_test_type, arrival_test_type)

    def get_pct_discovered_in_pre_departure(self):
        """Return the percentage of infections discovered in pre-departure."""
        x = [t.true_sensitivity for t in self.pre_departure_test_type]
        return np.array(x)

    def get_pct_discovered_in_arrival_test(self):
        """Return the percentage of infections discovered upon arrival."""
        x = [t.true_sensitivity for t in self.arrival_test_type]
        arrival_sensitivity = np.array(x)
        pct_undiscovered_in_pre_departure = \
            1 - self.get_pct_discovered_in_pre_departure()
        return pct_undiscovered_in_pre_departure * arrival_sensitivity


class TestingRegime:
    __test__ = False  # include so pytest ignores
    """
    This class maintains a testing regime.

    It offers methods to return the number of days someone is expected to be
    free and infectious, the infectious discovery rate, and the recovered
    discovery rate.
    """

    def __init__(self, test_type: List[Test], tests_per_week: np.ndarray):
        """Initialize a testing regime.

        Args:
            test_type (List[Test]): The test type to be used per meta-group.
            tests_per_week (np.ndarray): Test frequency per meta-group.
        """
        self.test_type = test_type
        self.tests_per_week = tests_per_week

    @staticmethod
    def from_dictionary(d: Dict, tests: Dict[str, Test]):
        """Initialize a [TestingRegime] instance.

        The dictionary [d] should contain a key [test_type] which contain list
        of strings. These are interpreted as keys in the [tests] dictionary
        which provides the corresponding [Test] instance.

        Args:
            d (Dict): Dictionary representing the testing regime.
            tests (Dict[str, Test]): Dictionary of [Test] instances.
        """
        test_type = [tests[i] for i in d["test_type"]]
        tests_per_week = np.array(d["tests_per_week"])
        return TestingRegime(test_type, tests_per_week)

    def get_days_infectious(self, max_infectious_days: float):
        """Return the expected number of days infectious.

        This value requires the context of the maximum infectious days.

        Args:
            max_infectious_days (float): Max days someone is infected."""
        ret = np.zeros(len(self.test_type))

        for i, (t, f) in enumerate(zip(self.test_type, self.tests_per_week)):
            days_between_tests = np.inf if f == 0 else 7 / f
            ret[i] = days_infectious(days_between_tests=days_between_tests,
                                     isolation_delay=t.test_delay,
                                     sensitivity=t.true_sensitivity,
                                     max_infectious_days=max_infectious_days)

        return ret

    def get_infection_discovery_frac(self, symptomatic_rate: float):
        """Return the discovery rate among infected people.

        This value is equivalent to the "true sensitivity" of a test when
        surveillance testing is in place. Otherwise, it is the test sensitivity
        multiplied by the symptomatic rate as only those that are symptomatic
        seek out a test. This assumes all symptomatic people will
        seek out a test. I.e. compliance among the symptomatic is 100%.

        Args:
            symptomatic_rate (float): Symptomatic rate.
        """
        infection_discovery_frac = np.zeros(len(self.test_type))
        for i, (t, f) in enumerate(zip(self.test_type, self.tests_per_week)):
            if f == 0:
                infection_discovery_frac[i] = \
                    symptomatic_rate * t.test_sensitivity
            else:
                infection_discovery_frac[i] = t.true_sensitivity
        return infection_discovery_frac

    def get_recovered_discovery_frac(self,
                                     no_surveillance_test_rate: np.ndarray):
        """Return the discovery rate among recovered people.

        This value is equivalent to the "true sensitivity" of a test when
        surveillance testing is in place. This serves as a rough
        estimate which becomes more inaccurate with less frequent testing.
        If there is no surveillance testing, it is the no surveillance test
        rate multiplied by the test sensitivity.

        Args:
            no_surveillance_test_rate (np.ndarray): Test rate per meta-group.
        """
        recovered_discovery_frac = np.zeros(len(self.test_type))
        for i, (t, f) in enumerate(zip(self.test_type, self.tests_per_week)):
            if f == 0:
                recovered_discovery_frac[i] = \
                    no_surveillance_test_rate[i] * t.test_sensitivity
            else:
                recovered_discovery_frac[i] = t.true_sensitivity
        return recovered_discovery_frac


class Strategy:
    """
    This class maintains a testing strategy comprised of an [IsolationRegime],
    [ArrivalTestingRegime], and a list of [TestingRegime]s.

    If offers methods to return the initial number of infections, the
    initial number of recovered, and the arrival discovered (useful for
    understanding isolation capacity needs).
    """

    def __init__(self, name: str, period_lengths: List[int],
                 testing_regimes: List[TestingRegime],
                 transmission_multipliers: List[float] = None,
                 arrival_testing_regime: ArrivalTestingRegime = None,
                 isolation_regime: IsolationRegime = None):
        """Initialize a testing strategy.

        Args:
            name (str): Name for this strategy.
            period_lengths (List[int]): Length (in generations) of each
                period of the simulation.
            testing_regimes (List[TestingRegime]): Testing regime to be used \
                in each period of the simulation.
            transmission_multipliers (List[float]): Transmission multiplier \
                to be used in each period of the simulation. Defaults to 1.
            arrival_testing_regime (ArrivalTestingRegime): Arrival testing \
                regime to be used. Defaults to None.
            isolation_regime (IsolationRegime): Isolation regime to be used. \
                Defaults to None.
        """
        self.name = name
        assert len(period_lengths) == len(testing_regimes)
        self.period_lengths = period_lengths
        self.testing_regimes = testing_regimes
        self.transmission_multipliers = transmission_multipliers
        self.arrival_testing_regime = arrival_testing_regime
        self.isolation_regime = isolation_regime

        if self.transmission_multipliers is None:
            self.transmission_multipliers = np.ones(len(period_lengths))

        if arrival_testing_regime is None:
            self.pct_discovered_in_pre_departure = 0
            self.pct_discovered_in_arrival_test = 0
        else:
            self.pct_discovered_in_pre_departure = \
                arrival_testing_regime.get_pct_discovered_in_pre_departure()
            self.pct_discovered_in_arrival_test = \
                arrival_testing_regime.get_pct_discovered_in_arrival_test()

    @staticmethod
    def from_dictionary(d: Dict, arrival_testing_regimes: Dict,
                        testing_regimes: Dict):
        """Initialize a [Strategy] instance.

        The dictionary [d] should contain a key [testing_regimes] and may
        contain a key [arrival_testing_regime]. These should be keys in
        [arrival_testing_regimes] and [testing_regimes] respectively.

        Args:
            d (Dict): Dictionary representing the strategy.
            arrival_testing_regimes (Dict): Dictionary of \
                [ArrivalTestingRegimes] instances.
            testing_regimes (Dict): Dictionary of [TestingRegimes] instances.
        """
        name = d["name"]
        period_lengths = np.array(d["period_lengths"])
        test_regimes = [testing_regimes[i] for i in d["testing_regimes"]]
        transmission_multipliers = d["transmission_multipliers"]
        if transmission_multipliers is not None:
            transmission_multipliers = np.array(transmission_multipliers)
        arrival_regime = d["arrival_testing_regime"]
        if arrival_regime is not None:
            arrival_regime = arrival_testing_regimes[arrival_regime]
        isolation_regime = d["isolation_regime"]
        if isolation_regime is not None:
            isolation_regime = \
                IsolationRegime.from_dictionary(isolation_regime)
        return Strategy(name, period_lengths, test_regimes,
                        transmission_multipliers, arrival_regime,
                        isolation_regime)

    def get_initial_infections(self, active_infections: np.ndarray):
        """Return the initial infections when this strategy is used.

        Args:
            active_infections (np.ndarray): True number of active infections \
                per meta-group.
        """
        pct_discovered = self.pct_discovered_in_pre_departure + \
            self.pct_discovered_in_arrival_test
        return (1 - pct_discovered) * active_infections

    def get_initial_recovered(self, recovered: np.ndarray,
                              active_infections: np.ndarray):
        """Return the initial recovered when this strategy is used.

        Args:
            recovered (np.ndarray): Recovered per meta-group.
            active_infections (np.ndarray): True number of active infections \
                per meta-group.
        """
        pct_discovered = self.pct_discovered_in_pre_departure + \
            self.pct_discovered_in_arrival_test
        return recovered + (pct_discovered * active_infections)

    def get_initial_discovered(self, recovered: np.ndarray,
                               pct_recovered_discovered: np.ndarray,
                               active_infections: np.ndarray):
        """Return the initial discovered when this strategy is used.

        Args:
            recovered (np.ndarray): Recovered per meta-group.
            pct_recovered_discovered (np.ndarray): Percentage of the \
                recovered population that is discovered per meta-group.
            active_infections (np.ndarray): True number of active infections \
                per meta-group.
        """
        inactive_discovered = recovered * pct_recovered_discovered
        pct_discovered = self.pct_discovered_in_pre_departure + \
            self.pct_discovered_in_arrival_test
        active_discovered = active_infections * pct_discovered
        return inactive_discovered + active_discovered

    def get_initial_hidden(self, recovered: np.ndarray,
                           pct_recovered_discovered: np.ndarray,
                           active_infections: np.ndarray):
        """Return the initial hidden when this strategy is used.

        Args:
            recovered (np.ndarray): Recovered per meta-group.
            pct_recovered_discovered (np.ndarray): Percentage of the \
                recovered population that is discovered per meta-group.
            active_infections (np.ndarray): True number of active infections \
                per meta-group.
        """
        inactive_hidden = recovered * (1 - pct_recovered_discovered)
        pct_discovered = self.pct_discovered_in_pre_departure + \
            self.pct_discovered_in_arrival_test
        active_hidden = active_infections * (1 - pct_discovered)
        return inactive_hidden + active_hidden


def strategies_from_dictionary(d: Dict, tests: Dict):
    """Return a dictionary of strategies.

    Args:
        d (Dict): Dictionary maintaining strategies.
        tests (Dict): Dictionary of test types used in the strategies.
    """
    arrival_regimes = \
        {k: ArrivalTestingRegime.from_dictionary(v, tests)
         for k,v in d["arrival_testing_regimes"].items()}
    testing_regimes = \
        {k: TestingRegime.from_dictionary(v, tests)
         for k,v in d["testing_regimes"].items()}
    strategies = \
        {k: Strategy.from_dictionary(v, arrival_regimes, testing_regimes)
         for k,v in d["strategies"].items()}
    return strategies
