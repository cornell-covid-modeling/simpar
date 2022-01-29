from strategy import ArrivalTestingRegime, TestingRegime, Strategy
from typing import Dict

# Based on the chosen Spring 2022 arrival testing regime described here:
# https://covid.cornell.edu/updates/20220112-testing-requirements.cfm

# Note: using antigen tests for arrival testing assumes simulation begins on
# or after January 18th
def sp22_arrival_testing(scenario: Dict):
    return ArrivalTestingRegime(scenario=scenario,
                                pre_departure_test_type="antigen",
                                arrival_test_type="antigen")

# UG: On-Campus: antigen, Off-campus: pcr (2x/week)
# GR/PR: On-Campus / PR: antigen (2x/week), Off-campus GR: (0x/week)
# FS: (0x/week)
def sp22_2x_week_testing_regime(scenario: Dict):
    return TestingRegime(scenario=scenario,
                         test_type={"UG_on": "antigen",
                                    "UG_off": "pcr",
                                    "GR_on": "antigen",
                                    "GR_off": "pcr",
                                    "PR_on": "antigen",
                                    "PR_off": "antigen",
                                    "FS": "pcr"},
                         tests_per_week={"UG_on": 2,
                                         "UG_off": 2,
                                         "GR_on": 2,
                                         "GR_off": 0,
                                         "PR_on": 2,
                                         "PR_off": 2,
                                         "FS": 0.25})   # @Peter

# UG: On-Campus: antigen, Off-campus: pcr (1x/week)
# GR/PR: On-Campus / PR: antigen (1x/week), Off-campus GR: (0x/week)
# FS: (0x/week)
def sp22_1x_week_testing_regime(scenario: Dict):
    return TestingRegime(scenario=scenario,
                         test_type="pcr",
                         tests_per_week={"UG_on": 1,
                                         "UG_off": 1,
                                         "GR_on": 1,
                                         "GR_off": 0,
                                         "PR_on": 1,
                                         "PR_off": 1,
                                         "FS": 0.25})   # @Peter

def no_testing_testing_regime(scenario: Dict):
    return TestingRegime(scenario=scenario, test_type="pcr", tests_per_week=0)

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


def sp22_no_testing_strategy(scenario: Dict):
    """Pre-departure + arrival testing. Surveillance of UG and professional
    students before classes and during virtual instruction at 2x/wk. It does
    not surveil GR or FS. After that, no testing."""
    T = scenario['T']
    CLASSWORK_TRANSMISSION_MULTIPLIER = \
        list(scenario['classwork_transmission_multiplier'].values())
    return \
        Strategy(name="UG+Prof. 2x/wk in Virtual Instr. Only",
                arrival_testing_regime=sp22_arrival_testing(scenario),
                testing_regimes=[sp22_2x_week_testing_regime(scenario),
                                 sp22_2x_week_testing_regime(scenario),
                                 sp22_2x_week_testing_regime(scenario),
                                 no_testing_testing_regime(scenario)],
                transmission_multipliers=[0.5,
                                          0.75,
                                          CLASSWORK_TRANSMISSION_MULTIPLIER,
                                          CLASSWORK_TRANSMISSION_MULTIPLIER],
                period_lengths=[1,1,4,T-6-1])


def sp22_1x_week_testing_strategy(scenario: Dict):
    """Pre-departure + arrival testing. Surveillance of UG and professional
    students before classes and during virtual instruction at 2x/wk. It does
    not surveil GR or FS. After that, move to 1x/wk testing."""
    T = scenario['T']
    CLASSWORK_TRANSMISSION_MULTIPLIER = \
        list(scenario['classwork_transmission_multiplier'].values())
    return \
        Strategy(name="UG+Prof. 2x/wk in Virtual Instr. 1x/wk After.",
                arrival_testing_regime=sp22_arrival_testing(scenario),
                testing_regimes=[sp22_2x_week_testing_regime(scenario),
                                 sp22_2x_week_testing_regime(scenario),
                                 sp22_2x_week_testing_regime(scenario),
                                 sp22_1x_week_testing_regime(scenario)],
                transmission_multipliers=[0.5,
                                          0.75,
                                          CLASSWORK_TRANSMISSION_MULTIPLIER,
                                          CLASSWORK_TRANSMISSION_MULTIPLIER],
                period_lengths=[1,1,4,T-6-1])
