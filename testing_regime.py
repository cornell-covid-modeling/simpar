import numpy as np
from typing import Union
from groups import meta_group, population
from micro import days_infectious
from typing import Dict
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

class TestingRegime:
    def get_days_infectious(self):
        return self.days_infectious

    def get_infection_discovery_frac(self):
        return self.infection_discovery_frac

    def get_recovered_discovery_frac(self):
        return self.recovered_discovery_frac

    def get_name(self):
        return self.name

    def __init__(self,
                 scenario: Dict,
                 tests_per_week: Union[float, dict],
                 test_delay: Union[float, dict]):

        popul = population.from_scenario(scenario)

        K = len(popul.metagroup_names()) # number of meta-groups
        self.days_infectious = np.zeros(K)
        self.infection_discovery_frac = np.zeros(K)
        self.recovered_discovery_frac = np.zeros(K)

        # Name the testing regime
        if tests_per_week == 0: # No surveillance
            self.name = "No surveillance"
        elif np.isscalar(tests_per_week) and np.isscalar(test_delay):
            self.name = "%dx/wk, %.1fd delay" % (tests_per_week, test_delay)
        else:
            self.name = ''
            for mg in popul.metagroup_names():
                if np.isscalar(tests_per_week):
                    _tests_per_week = tests_per_week
                else:
                    _tests_per_week = tests_per_week[mg]
                if np.isscalar(test_delay):
                    _test_delay = test_delay
                else:
                    _test_delay = test_delay[mg]

                if _tests_per_week > 0:
                    self.name = self.name + 'mg: %dx/wk %.1fd delay ' % (_tests_per_week, _test_delay)
                else:
                    self.name = self.name + 'mg: no surveillance'


        mg_names = popul.metagroup_names()
        for i in range(len(mg_names)):

            # Extract tests per week and test delay from the function arguments for this meta-group
            if isinstance(tests_per_week, dict):
                _tests_per_week = tests_per_week[mg_names[i]]
            else:
                _tests_per_week = tests_per_week
            if isinstance(test_delay, dict):
                _test_delay = test_delay[mg_names[i]]
            else:
                _test_delay = test_delay

            # Figure out days between tests, infection_discovery_frac, and recovered_discovery frac
            # for this meta-group
            if _tests_per_week == 0:
                _days_between_tests = np.inf
                self.infection_discovery_frac[i] = scenario["symptomatic_rate"]
                self.recovered_discovery_frac[i] = scenario["no_surveillance_test_rate"]
            else:
                _days_between_tests = 7 / _tests_per_week
                self.infection_discovery_frac[i] = 1
                self.recovered_discovery_frac[i] = 1

            self.days_infectious[i] = days_infectious(_days_between_tests, _test_delay, \
                                                 sensitivity=scenario["pcr_sensitivity"], \
                                                 max_infectious_days=scenario["max_infectious_days"])