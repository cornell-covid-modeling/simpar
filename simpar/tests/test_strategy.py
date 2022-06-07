from ast import Str
import numpy as np
from simpar.micro import days_infectious
from simpar.strategy import Test, ArrivalTestingRegime, TestingRegime, Strategy


TESTS = {
    "pcr": {
        "sensitivity": 0.8,
        "test_delay": 1.5,
        "compliance": 0.9
    },
    "antigen": {
        "sensitivity": 0.6,
        "test_delay": 0,
        "compliance": 0.5
    },
}

def get_test(name):
    return Test.from_dictionary(name, TESTS[name])


def test_test_initialization():
    """Test initialization of [Test] class from dictionary."""
    test = get_test("pcr")
    assert test.name == "pcr"
    assert test.sensitivity == 0.8
    assert test.test_delay == 1.5
    assert test.compliance == 0.9


def test_arrival_testing_regime_single_meta_group():
    """Test [ArrivalTestingRegime] class with one meta-group."""
    pre_departure_test = [get_test("antigen")]
    arrival_test = [get_test("pcr")]
    regime = ArrivalTestingRegime(pre_departure_test, arrival_test)

    assert np.isclose(regime.get_pct_discovered_in_pre_departure(), [0.3])
    assert np.isclose(regime.get_pct_discovered_in_arrival_test(), [0.504])


def test_arrival_testing_regime_three_meta_groups():
    """Test [ArrivalTestingRegime] class with three meta-groups."""
    pcr = get_test("pcr")
    antigen = get_test("antigen")
    pre_departure_test = [antigen, pcr, antigen]
    arrival_test = [pcr, pcr, antigen]
    regime = ArrivalTestingRegime(pre_departure_test, arrival_test)

    assert np.isclose(regime.get_pct_discovered_in_pre_departure(),
                      np.array([0.3, 0.72, 0.3])).all()
    assert np.isclose(regime.get_pct_discovered_in_arrival_test(),
                      np.array([0.504, 0.2016, 0.21])).all()


def test_testing_regime_one_meta_group_with_testing():
    """Test [TestingRegime] class with one meta-group with testing."""
    test_type = [get_test("pcr")]
    tests_per_week = np.array([2])
    regime = TestingRegime(test_type, tests_per_week)
    R = 5
    expected = days_infectious(days_between_tests=3.5, isolation_delay=1.5,
                               sensitivity=0.8, max_infectious_days=R)
    assert regime.get_days_infectious(max_infectious_days=5) == expected
    # TODO this may change after discussing with Peter
    assert regime.get_infection_discovery_frac(0.3) == [1]
    assert regime.get_recovered_discovery_frac(0) == [1]


def test_testing_regime_one_meta_group_no_testing():
    """Test [TestingRegime] class with one meta-group without testing."""
    test_type = [get_test("pcr")]
    tests_per_week = np.array([0])
    regime = TestingRegime(test_type, tests_per_week)
    R = 5
    expected = days_infectious(days_between_tests=np.inf, isolation_delay=1.5,
                               sensitivity=0.8, max_infectious_days=R)
    assert regime.get_days_infectious(max_infectious_days=5) == expected
    # TODO this may change after discussing with Peter
    assert regime.get_infection_discovery_frac(0.3) == 0.3
    assert regime.get_recovered_discovery_frac(0.4) == [0.4]


def test_testing_regime_three_meta_groups():
    """Test [TestingRegime] class with three meta-group."""
    pcr = get_test("pcr")
    antigen = get_test("antigen")
    test_type = [antigen, pcr, antigen]
    tests_per_week = np.array([0, 2, 2])
    regime = TestingRegime(test_type, tests_per_week)
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
    assert np.isclose(regime.get_recovered_discovery_frac(0.7),
                      np.array([0.7, 1, 1])).all()


def test_strategy():
    """Test [Strategy] class with three meta-groups."""
    pcr = get_test("pcr")
    antigen = get_test("antigen")

    pre_departure_test = [antigen, pcr, antigen]
    arrival_test = [pcr, pcr, antigen]
    arrival_regime = ArrivalTestingRegime(pre_departure_test, arrival_test)

    test_type = [antigen, pcr, antigen]
    tests_per_week = np.array([0, 2, 2])
    testing_regime = TestingRegime(test_type, tests_per_week)

    strategy = Strategy(name="test", period_lengths=[5,5],
                        testing_regimes=[testing_regime, testing_regime],
                        transmission_multipliers=[1, 0.75],
                        arrival_testing_regime=arrival_regime)

    pct_discovered_in_pre_departure =  np.array([0.3, 0.72, 0.3])
    pct_discovered_in_arrival_test = np.array([0.504, 0.2016, 0.21])
    pct_discovered = \
        pct_discovered_in_pre_departure + pct_discovered_in_arrival_test

    active_infections = np.array([1, 3, 2])
    expected = active_infections * (1 - pct_discovered)
    value = strategy.get_initial_infections(active_infections)
    assert np.isclose(value, expected).all()

    recovered = np.array([5, 10, 6])
    expected = recovered + active_infections * pct_discovered
    value = strategy.get_initial_recovered(recovered, active_infections)
    assert np.isclose(value, expected).all()

    pct_recovered_discovered_on_arrival = 0.5 * np.ones(3)
    expected = (pct_discovered_in_arrival_test * active_infections) + \
        (pct_recovered_discovered_on_arrival * recovered)
    val = strategy.get_arrival_discovered(recovered, active_infections,
                                          pct_recovered_discovered_on_arrival)
    assert np.isclose(val, expected).all()
