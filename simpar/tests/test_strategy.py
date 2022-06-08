import os
import yaml
import numpy as np
from simpar.micro import days_infectious
from simpar.strategy import (Test, ArrivalTestingRegime, TestingRegime,
                             strategies_from_dictionary)


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')
with open(os.path.join(RESOURCES_PATH, "test_strategy.yaml"), "r") as f:
    yaml_file = yaml.safe_load(f)
    tests = yaml_file["tests"]
    TESTS = {k: Test.from_dictionary(k, v) for k,v in tests.items()}
    arrival_testing_regimes = yaml_file["arrival_testing_regimes"]
    ARRIVAL_TESTING_REGIMES = \
        {k: ArrivalTestingRegime.from_dictionary(v, TESTS)
         for k,v in arrival_testing_regimes.items()}
    testing_regimes = yaml_file["testing_regimes"]
    TESTING_REGIMES = \
        {k: TestingRegime.from_dictionary(v, TESTS)
         for k,v in testing_regimes.items()}
    STRATEGY = strategies_from_dictionary(yaml_file, TESTS)["test"]


def test_test_initialization():
    """Test initialization of [Test] class from dictionary."""
    test = TESTS["pcr"]
    assert test.name == "pcr"
    assert test.sensitivity == 0.8
    assert test.test_delay == 1.5
    assert test.compliance == 0.9


def test_arrival_testing_regime_single_meta_group():
    """Test [ArrivalTestingRegime] class with one meta-group."""
    regime = ARRIVAL_TESTING_REGIMES["single_meta_group"]
    assert np.isclose(regime.get_pct_discovered_in_pre_departure(), [0.3])
    assert np.isclose(regime.get_pct_discovered_in_arrival_test(), [0.504])


def test_arrival_testing_regime_three_meta_groups():
    """Test [ArrivalTestingRegime] class with three meta-groups."""
    regime = ARRIVAL_TESTING_REGIMES["three_meta_groups"]
    assert np.isclose(regime.get_pct_discovered_in_pre_departure(),
                      np.array([0.3, 0.72, 0.3])).all()
    assert np.isclose(regime.get_pct_discovered_in_arrival_test(),
                      np.array([0.504, 0.2016, 0.21])).all()


def test_testing_regime_one_meta_group_with_testing():
    """Test [TestingRegime] class with one meta-group with testing."""
    regime = TESTING_REGIMES["single_meta_group_with_testing"]
    R = 5
    expected = days_infectious(days_between_tests=3.5, isolation_delay=1.5,
                               sensitivity=0.8, max_infectious_days=R)
    assert regime.get_days_infectious(max_infectious_days=5) == expected
    # TODO this may change after discussing with Peter
    assert regime.get_infection_discovery_frac(0.3) == [1]
    assert regime.get_recovered_discovery_frac(np.array([0])) == [1]


def test_testing_regime_one_meta_group_no_testing():
    """Test [TestingRegime] class with one meta-group without testing."""
    regime = TESTING_REGIMES["single_meta_group_no_testing"]
    R = 5
    expected = days_infectious(days_between_tests=np.inf, isolation_delay=1.5,
                               sensitivity=0.8, max_infectious_days=R)
    assert regime.get_days_infectious(max_infectious_days=5) == expected
    # TODO this may change after discussing with Peter
    assert regime.get_infection_discovery_frac(0.3) == 0.3
    assert regime.get_recovered_discovery_frac(np.array([0.4])) == [0.4]


def test_testing_regime_three_meta_groups():
    """Test [TestingRegime] class with three meta-group."""
    regime = TESTING_REGIMES["three_meta_groups"]
    R = 5

    expected = [
        days_infectious(days_between_tests=np.inf, isolation_delay=0,
                        sensitivity=0.6, max_infectious_days=R),
        days_infectious(days_between_tests=3.5, isolation_delay=1.5,
                        sensitivity=0.8, max_infectious_days=R),
        days_infectious(days_between_tests=3.5, isolation_delay=0,
                        sensitivity=0.6, max_infectious_days=R)
    ]

    assert np.isclose(regime.get_days_infectious(max_infectious_days=5),
                      np.array(expected)).all()
    # TODO this may change after discussing with Peter
    assert np.isclose(regime.get_infection_discovery_frac(0.3),
                      np.array([0.3, 1, 1])).all()
    no_surveil_rate = np.array([0.7, 0.8, 0.6])
    assert np.isclose(regime.get_recovered_discovery_frac(no_surveil_rate),
                      np.array([0.7, 1, 1])).all()


def test_strategy():
    """Test [Strategy] class with three meta-groups."""
    pct_discovered_in_pre_departure = np.array([0.3, 0.72, 0.3])
    pct_discovered_in_arrival_test = np.array([0.504, 0.2016, 0.21])
    pct_discovered = \
        pct_discovered_in_pre_departure + pct_discovered_in_arrival_test

    active_infections = np.array([1, 3, 2])
    expected = active_infections * (1 - pct_discovered)
    value = STRATEGY.get_initial_infections(active_infections)
    assert np.isclose(value, expected).all()

    recovered = np.array([5, 10, 6])
    expected = recovered + active_infections * pct_discovered
    value = STRATEGY.get_initial_recovered(recovered, active_infections)
    assert np.isclose(value, expected).all()

    pct_recovered_discovered_on_arrival = 0.5 * np.ones(3)
    expected = (pct_discovered_in_arrival_test * active_infections) + \
        (pct_recovered_discovered_on_arrival * recovered)
    val = STRATEGY.get_arrival_discovered(recovered, active_infections,
                                          pct_recovered_discovered_on_arrival)
    assert np.isclose(val, expected).all()
