"""SIR-style model simulation.

The module defines a [Sim] class. The class is initialized with base parameters
for the simulation. The [step] method allows one to step through the
simulation one or many time periods at a time. Infection spread and discovery
parameters can be specified and the base parameters are used by default.
"""

__author__ = "Peter Frazier (peter-i-frazier)"

import numpy as np
from typing import Union, Dict


class Sim:
    """
    Maintains an SIR-style model simulation on a heterogeneous population.

    Infections last a single generation, after which people recover and are
    immune for the remainder of the simulation. Infections may be discovered
    immediately (e.g., through symptomatic self-reporting or surveillance) or
    may be discovered later (e.g., because of an asymptomatic test applied to
    the whole population).

    During execution, S, I, and R are TxK matrices that track the number of
    susceptible, infectious, and recovered people in each of the K groups over
    T time periods. Additionally, D and H track the number of discovered and
    hidden non-susceptible people.
    """

    def __init__(self, max_T: int, init_susceptible: np.ndarray,
                 init_infected: np.ndarray, init_recovered: np.ndarray,
                 infection_rate: np.ndarray,
                 init_discovered: np.ndarray = None,
                 init_hidden: np.ndarray = None,
                 infection_discovery_frac: Union[float,np.ndarray] = 1,
                 recovered_discovery_frac: Union[float,np.ndarray] = 1,
                 outside_rate: np.ndarray = 0):
        """Initialize an SIR-style model simulation.

        The initial state of the simulation is passed through the
        [init_susceptible], [init_infected], and [init_recovered] parameters.
        The [init_discovered] and [init_hidden] are optional parameters. If
        they are not set, the initial discovered and hidden assumes all
        recovered are discovered and [infection_discovery_frac] of infected
        are discovered.

        Internal infection spread is determined by the [infection_rate] matrix
        parameter which indicates the number new infections that an infected
        person in one group creates in another. Additionally, the
        [outside_rate] parameter specifies the outside rate of infection.

        To model infection discovery, the [infection_discovery_frac]
        parameter determines what fraction of infected are discovered in the
        generation they are infected. Otherwise, they become "hidden
        recovered." Furthermore, the [recovered_discovery_frac] parameter
        determines what fraction of hidden recovered infections are discovered
        in each generation.

        Args:
            max_T (int): Maximum number of time periods to simulate.
            init_susceptible (np.ndarray): Vector of the initial number of \
                people in each group that are susceptible.
            init_infected (np.ndarray): Vector of the initial number of \
                people in each group that are infected.
            init_recovered (np.ndarray): Vector of the initial number of \
                people in each group that are recovered.
            infection_rate (np.ndarray): Matrix where infection_rate[i,j] is \
                the number of new infections that an infected person in \
                group i creates in group j
            init_discovered (np.ndarray): Vector of the initial number of \
                people in each group that are discovered.
            init_hidden (np.ndarray): Vector of the initial number of \
                people in each group that are hidden.
            infection_discovery_frac (float or np.ndarray): Fraction of \
                infections discovered in the generation they are infected.
                Can be specified globally (as a float) or separately for \
                each group (as a np.ndarray). Defaults to 1.
            recovered_discovery_frac (float or np.ndarray): Fraction of \
                hidden recovered discovered in each generation. Can be \
                specified globally (as a float) or separately for each group \
                (as a np.ndarray). Defaults to 1.
            outside_rate (np.ndarray): infections per time period, weighed by \
                population of each group in a meta-group.
        """
        assert (max_T > 0)
        self.max_T = max_T  # number of periods to simulate
        self._t = 0

        self.K = len(init_susceptible)  # number of groups
        assert (len(init_infected) == self.K)
        assert (len(init_recovered) == self.K)

        self.infection_discovery_frac =  \
            self._validate_discovery_frac(infection_discovery_frac, self.K)
        self.recovered_discovery_frac =  \
            self._validate_discovery_frac(recovered_discovery_frac, self.K)

        assert ((init_susceptible >= 0).all())
        assert ((init_infected >= 0).all())
        assert ((init_recovered >= 0).all())

        self._S = np.zeros((self.max_T+1, self.K))  # susceptible
        self._I = np.zeros((self.max_T+1, self.K))  # infected
        self._R = np.zeros((self.max_T+1, self.K))  # recovered
        self._D = np.zeros((self.max_T+1, self.K))  # discovered
        self._H = np.zeros((self.max_T+1, self.K))  # hidden

        self._S[0] = init_susceptible
        self._I[0] = init_infected
        self._R[0] = init_recovered

        if init_discovered is None:
            self._D[0] = self._R[0] + \
                (self._I[0] * self.infection_discovery_frac)
        else:
            self._D[0] = init_discovered

        if init_hidden is None:
            self._H[0] = self._I[0] * (1 - self.infection_discovery_frac)
        else:
            self._H[0] = init_hidden

        initial_IR = self._I[0] + self._R[0]
        initial_DH = self._D[0] + self._H[0]
        assert np.isclose(initial_IR, initial_DH).all()

        self.infection_rate = infection_rate
        self.outside_rate = outside_rate

    @staticmethod
    def from_dictionary(d: Dict):
        """Initialize an instance of Sim from a dictionary."""
        T = d["T"]
        S0 = np.array(d["S0"])
        I0 = np.array(d["I0"])
        R0 = np.array(d["R0"])
        D0 = None if d["D0"] is None else np.array(d["D0"])
        H0 = None if d["H0"] is None else np.array(d["H0"])
        infection_rate = np.array(d["infection_rate"])
        infection_discovery_frac = np.array(d["infection_discovery_frac"])
        recovered_discovery_frac = np.array(d["recovered_discovery_frac"])
        outside_rate = np.array(d["outside_rate"])
        return Sim(max_T=T, init_susceptible=S0, init_infected=I0,
                   init_recovered=R0, infection_rate=infection_rate,
                   init_discovered=D0, init_hidden=H0,
                   infection_discovery_frac=infection_discovery_frac,
                   recovered_discovery_frac=recovered_discovery_frac,
                   outside_rate=outside_rate)

    @property
    def S(self):
        return self._S.copy()

    @S.setter
    def S(self, value):
        self._S = value

    @property
    def I(self):
        return self._I.copy()

    @I.setter
    def I(self, value):
        self._I = value

    @property
    def R(self):
        return self._R.copy()

    @R.setter
    def R(self, value):
        self._R = value

    @property
    def D(self):
        return self._D.copy()

    @D.setter
    def D(self, value):
        self._D = value

    @property
    def H(self):
        return self._H.copy()

    @H.setter
    def H(self, value):
        self._H = value

    def step(self, n: int = 1, infection_rate: np.ndarray = None,
             infection_discovery_frac: Union[float,np.ndarray] = None,
             recovered_discovery_frac: Union[float,np.ndarray] = None,
             outside_rate: np.ndarray = None):
        """Take [n] steps forward in the simulation.

        To model change in infection and discovery parameters over time, these
        parameters can be provided to be applied to the next [n] time periods.

        Args:
            infection_rate (np.ndarray): Matrix where infection_rate[i,j] is \
                the number of new infections that an infected person in \
                group i creates in group j
            infection_discovery_frac (float or np.ndarray): Fraction of \
                infections discovered in the generation they are infected.
                Can be specified globally (as a float) or separately for \
                each group (as a np.ndarray). Defaults to 1.
            recovered_discovery_frac (float or np.ndarray): Fraction of \
                hidden recovered discovered in each generation. Can be \
                specified globally (as a float) or separately for each group \
                (as a np.ndarray). Defaults to 1.
            outside_rate (np.ndarray): infections per time period, weighed by \
                population of each group in a meta-group.
        """
        assert(n >= 1)
        if n > 1:
            for _ in range(n):
                self.step(infection_rate=infection_rate,
                          infection_discovery_frac=infection_discovery_frac,
                          recovered_discovery_frac=recovered_discovery_frac,
                          outside_rate=outside_rate)
            return

        if infection_rate is None:
            infection_rate = self.infection_rate

        if infection_discovery_frac is None:
            infection_discovery_frac = self.infection_discovery_frac
        else:
            infection_discovery_frac = \
                self._validate_discovery_frac(infection_discovery_frac, self.K)

        if recovered_discovery_frac is None:
            recovered_discovery_frac = self.recovered_discovery_frac
        else:
            recovered_discovery_frac = \
                self._validate_discovery_frac(recovered_discovery_frac, self.K)

        if outside_rate is None:
            outside_rate = self.outside_rate

        t = self._t

        assert(t < self.max_T)  # enforce max generation

        # Fraction susceptible in each group
        # self._S[t] / (self._S[t] + self._I[t] + self._R[t])
        frac_susceptible = \
            np.divide(self._S[t], (self._S[t] + self._I[t] + self._R[t]),
                      out=np.zeros_like(self._S[t]),
                      where=(self._S[t] + self._I[t] + self._R[t]) != 0)

        # Infected from internal spread and outside rate
        self._I[t+1] = np.matmul(self._I[t], infection_rate) * frac_susceptible
        self._I[t+1] += frac_susceptible * outside_rate
        # Can not infect more than the infected number of people
        self._I[t+1] = np.minimum(self._I[t+1], self._S[t])

        # Set susceptible to reflect those that were infected and set
        # recovered to be the number of people previously infected
        self._S[t+1] = self._S[t] - self._I[t+1]
        self._R[t+1] = self._R[t] + self._I[t]

        # Discover some fraction of hidden recoveries
        self._D[t+1] = \
            self._D[t] + np.multiply(self._H[t], recovered_discovery_frac)
        self._H[t+1] = np.multiply(self._H[t], 1 - recovered_discovery_frac)

        # Discover some fraction of those infected in this time period
        self._D[t+1] += np.multiply(self._I[t+1], infection_discovery_frac)
        self._H[t+1] += np.multiply(self._I[t+1], 1-infection_discovery_frac)

        self._t = self._t + 1  # move time forward by one step

        return self

    @staticmethod
    def _validate_discovery_frac(x, K):
        """Return validated discovery fraction vector."""
        if np.isscalar(x):
            x = x * np.ones(K)
        assert (x >= 0).all()
        assert (x <= 1).all()
        return x
