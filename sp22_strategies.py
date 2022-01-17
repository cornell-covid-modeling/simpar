from strategy import ArrivalTestingRegime, TestingRegime, Strategy
from typing import Dict

# ========================================================
# Define testing regimes used by potential sp22 strategies
# ========================================================

# TODO (hwr): Update this to reflect actual sp22 policy
def sp22_arrival_testing(scenario: Dict):
    return ArrivalTestingRegime(scenario=scenario,
                                pre_departure_test_type="antigen",
                                arrival_test_type="pcr")

def no_testing_testing_regime(scenario: Dict):
    return TestingRegime(scenario=scenario, test_type="pcr", tests_per_week=0, test_delay=1)

def ug_prof_2x_week_testing_regime(scenario: Dict):
    return TestingRegime(scenario=scenario,
                         test_type="pcr",
                         tests_per_week={ 'UG':2, 'GR':0, 'PR':2, 'FS':0},
                         test_delay=1.5)

# =========================
# Potential sp22 strategies
# =========================

def no_testing_strategy(scenario: Dict):
    T = scenario['T']
    CLASSWORK_TRANSMISSION_MULTIPLIER = \
        list(scenario['classwork_transmission_multiplier'].values())
    return \
        Strategy(name="No Testing",
            arrival_testing_regime=None,
            testing_regimes=[no_testing_testing_regime(scenario),
                             no_testing_testing_regime(scenario)],
            transmission_multipliers=[1, CLASSWORK_TRANSMISSION_MULTIPLIER],
            period_lengths=[3,T-3-1])


def arrival_testing_strategy(scenario: Dict):
    """Pre-departure + arrival testing. No surveillance at any point"""
    T = scenario['T']
    CLASSWORK_TRANSMISSION_MULTIPLIER = \
        list(scenario['classwork_transmission_multiplier'].values())
    return \
        Strategy(name="Only Pre-Departure + Arrival Testing",
            arrival_testing_regime=sp22_arrival_testing(scenario),
            testing_regimes=[no_testing_testing_regime(scenario),
                             no_testing_testing_regime(scenario)],
            transmission_multipliers=[1, CLASSWORK_TRANSMISSION_MULTIPLIER],
            period_lengths=[3,T-3-1])


def surge_testing_strategy(scenario: Dict):
    """ Pre-departure + arrival testing. Surveillance of UG and professional
    students before classes and during virtual instruction at 2x/wk. It does
    not surveil GR or FS."""
    T = scenario['T']
    CLASSWORK_TRANSMISSION_MULTIPLIER = \
        list(scenario['classwork_transmission_multiplier'].values())
    return \
        Strategy(name="UG+Prof. 2x/wk in Virtual Instr. Only",
                arrival_testing_regime=sp22_arrival_testing(scenario),
                testing_regimes=[ug_prof_2x_week_testing_regime(scenario),
                                 ug_prof_2x_week_testing_regime(scenario),
                                 no_testing_testing_regime(scenario)],
                transmission_multipliers=[1,
                                          CLASSWORK_TRANSMISSION_MULTIPLIER,
                                          CLASSWORK_TRANSMISSION_MULTIPLIER],
                period_lengths=[3,3,T-6-1])
