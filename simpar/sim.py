import numpy as np
from isolation import compute_isolated
from typing import Union

class sim:
    '''
    Simulates COVID in a population using a SIR-style model.
    Infections last a single generation, after which people recover and are immune for the remainder of the simulation.
    Infections may be discovered immediately (e.g., through symptomatic self-reporting or surveillance) or may be
    discovered later (e.g., because of a 1-time asymptomatic test applied to the whole population, or because the
    student had symptoms due to another cause and got a COVID test).

    Supports multiple groups. Takes as input a matrix (infection_matrix) that determines the number of secondary
    infections created in each group j over 1 generation by a single infection in group i.

    Appropriate choices for this matrix can be determined using the micro class.  This takes as input testing
    interventions as well as social and biological parameters to produce this matrix.

    During execution, S, I, and R are TxK matrices that track the number susceptible, infectious, and recovered in each
    of the K groups over T time periods.
    '''
    def __init__(self, max_T: int, init_susceptible: np.ndarray,
                 init_infected: np.ndarray, init_recovered: np.ndarray,
                 infection_rate: np.ndarray,
                 infection_discovery_frac: Union[float,np.ndarray] = 1,
                 recovered_discovery_frac: Union[float,np.ndarray] = 1,
                 generation_time: float = 1,
                 outside_rate = 0):
        """Initialize an SIR-style simulation of COVID spread.

        Group dynamics can be captured by providing vectors of
        initial counts. If there are K groups, the length of init_susceptible,
        init_infected, and init_recovered should all be K.

        To model the discovery of people who
        have or had COVID (I or R), we model a fraction infection_discovery_frac
        of new infections as being discovered in the generation that they start.
        If they are not discovered then, they become "hidden recovered".  A
        fraction recovered_discovery_frac of the undiscovered recovered infections
        are discovered in each generation.

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
            infection_discovery_frac (float or np.ndarray): Fraction of \
                infections discovered in the generation that they start.
                Can be specified globally (as a float) or separately for \
                each group (as a np.ndarray). Defaults to 1.
            recovered_discovery_frac (float or np.ndarray): Fraction of recovered \
                discovered in each generation. Can be specified globally (as a float) \
                or separately for each group (as a np.ndarray). Defaults to 1.
            generation_time (float): Length of the generation interval in \
                whatever units the user would like to use, e.g., days or weeks. \
                This is not used, except to support plotting. Defaults to 1.
            outside_rate: infections per day, weighed by population of each \
                group in a meta-group.
        """
        assert (max_T > 0)

        self.max_T = max_T # Maximum number of periods we can simulate
        self.t = 0 # current time period
        self.generation_time = generation_time

        self.K = len(init_susceptible) # Number of groups
        assert (len(init_infected) == self.K)
        assert (len(init_recovered) == self.K)

        if np.isscalar(infection_discovery_frac):
            infection_discovery_frac = infection_discovery_frac * np.ones(self.K)

        if np.isscalar(recovered_discovery_frac):
            recovered_discovery_frac = recovered_discovery_frac * np.ones(self.K)

        assert (infection_discovery_frac >= 0).all()
        assert (infection_discovery_frac <= 1).all()
        assert (recovered_discovery_frac >= 0).all()
        assert (recovered_discovery_frac <= 1).all()

        self.infection_discovery_frac = infection_discovery_frac
        self.recovered_discovery_frac = recovered_discovery_frac

        self.S = np.zeros((self.max_T, self.K)) # susceptible
        self.I = np.zeros((self.max_T, self.K)) # infected
        self.R = np.zeros((self.max_T, self.K)) # recovered
        self.D = np.zeros((self.max_T, self.K)) # discovered infections
        self.H = np.zeros((self.max_T, self.K)) # hidden recovered infections

        self.I[0] = init_infected
        self.S[0] = init_susceptible
        self.R[0] = init_recovered

        self.D[0] = np.multiply(self.I[0],self.infection_discovery_frac) # elementwise multiplication
        self.H[0] = np.multiply(self.I[0],1-self.infection_discovery_frac) # elementwise multiplication

        assert ((init_susceptible >= 0).all())
        assert ((init_infected >= 0).all())
        assert ((init_recovered >= 0).all())

        assert (infection_rate.shape == (self.K, self.K))
        self.infection_rate = infection_rate
        self.outside_rate = outside_rate


    def step(self, nsteps: int = 1, infection_rate: np.ndarray = None,
             infection_discovery_frac: Union[float,np.ndarray] = None,
             recovered_discovery_frac: Union[float,np.ndarray] = None,
             outside_rate = None):
        """Take n steps forward in the simulation.

        As parameters like infection_rate can change over time, this function
        can take those parameters as input.

        Args:
            infection_rate (np.ndarray): Matrix where infection_rate[i,j] is \
                the number of new infections that an infected person in \
                group i creates in group j. Defaults to self.infection_rate.
            infection_discovery_frac (float or np.ndarray): Fraction of \
                infections discovered in the generation that they start.
                Can be specified globally (as a float) or separately for \
                each group (as a np.ndarray). Defaults to 1.
            recovered_discovery_frac (float or np.ndarray): Fraction of recovered \
                discovered in each generation. Can be specified globally (as a float) \
                or separately for each group (as a np.ndarray). Defaults to 1.
        """
        assert(nsteps >= 1)
        # take multiple steps if necessary
        if nsteps > 1:
            for _ in range(nsteps):
                self.step(infection_rate=infection_rate,
                          infection_discovery_frac=infection_discovery_frac,
                          recovered_discovery_frac=recovered_discovery_frac)
            return

        if infection_rate is None:
            infection_rate = self.infection_rate

        if infection_discovery_frac is None:
            infection_discovery_frac = self.infection_discovery_frac
        elif np.isscalar(infection_discovery_frac):
            infection_discovery_frac = infection_discovery_frac * np.ones(self.K)
        assert (infection_discovery_frac >= 0).all()
        assert (infection_discovery_frac <= 1).all()

        if recovered_discovery_frac is None:
            recovered_discovery_frac = self.recovered_discovery_frac
        elif np.isscalar(recovered_discovery_frac):
            recovered_discovery_frac = recovered_discovery_frac * np.ones(self.K)
        assert (recovered_discovery_frac >= 0).all()
        assert (recovered_discovery_frac <= 1).all()

        if outside_rate is None:
            outside_rate = self.outside_rate

        t = self.t

        assert(t+1 < self.max_T) # enforce max generation

        # vector giving the fraction susceptible in each group
        frac_susceptible = np.divide(self.S[t], (self.S[t] + self.I[t] + self.R[t]), out=np.zeros_like(self.S[t]), where=(self.S[t] + self.I[t] + self.R[t])!=0) # self.S[t] / (self.S[t] + self.I[t] + self.R[t])

        # The number of new infections in each group that would result, if everyone were susceptible
        # A = I[t-1] is a vector containing the number of infections in each source group
        # np.matmul(A, infection_rate) has a value at entry j of sum(A[k], infection_rate[k,j])
        self.I[t+1] = np.matmul(self.I[t], infection_rate)

        # Adjust this for the fact that not everyone is susceptible. This is an elementwise product.
        self.I[t+1] = self.I[t+1] * frac_susceptible

        # Inject outside infections, only susceptible
        self.I[t+1] += frac_susceptible * self.generation_time * outside_rate

        # We can't infect more than the number of susceptible people.
        # np.minimum applied to two arrays returns the elementwise minimum.
        self.I[t+1] = np.minimum(self.I[t+1],self.S[t])

        # Move the infected people out of susceptible and in to recovered
        self.S[t+1] = self.S[t]-self.I[t+1]
        self.R[t+1] = self.R[t]+self.I[t]

        # The old hidden recoveries are either discovered (with probability recovered_discovery_frac) or move forward
        # into the next time period as hidden recoveries. np.multiply is elementwise multiplication.
        self.D[t+1] = np.multiply(self.H[t],recovered_discovery_frac) # discovery of old hidden recoveries
        self.H[t+1] = np.multiply(self.H[t],1-recovered_discovery_frac)

        # New infections are either discovered immediately (with probability infection_discovery_frac) or
        # become hidden recoveries.
        self.D[t+1] = self.D[t+1] + np.multiply(self.I[t+1], infection_discovery_frac)
        self.H[t+1] = self.H[t+1] + np.multiply(self.I[t+1], 1-infection_discovery_frac)

        self.t = self.t + 1 # Move time forward by one step

        return self

    def __get_metric__(self,metric):
        if metric == 'S':
            return self.S
        elif metric == 'I':
            return self.I
        elif metric == 'R':
            return self.R
        elif metric == 'D':
            return self.D
        elif metric == 'H':
            return self.H
        else:
            raise ValueError('metric argument must be one of S,I,R,D,H')

    def get_metric_for_different_groups(self, metric, group, normalize = False, cumulative = False):
        '''
        Returns a matrix where [t, i] entry contains the number of people in group[i] of a particular type (S,I,R,D,H)
        in generation t. If normalize is true, then this is normalized to the group's population
        size.  For example, to get a vector containing the number of people with an active infection in groups [0, 1] and
        each generation, call get_metric_for_different_groups('I', [0, 1]).
        '''
        assert(len(group)>0)
        assert(min(group) >= 0)
        assert(max(group) < self.K)

        y = self.__get_metric__(metric)[:,group]

        if normalize:
            pop = self.S[:, group] + self.I[:, group] + self.R[:, group]  # total population by time
            y = y / pop

        if cumulative:
            return np.cumsum(y, axis=0)
        else:
            return y

    def get_metric_for_group(self, metric, group_idxs, normalize = False, cumulative = False):
        '''
        Returns a vector where component t contains the number of people of a particular type (S,I,R,D,H)
        in generation t in a specific set of group. If normalize is true, then this is normalized to the group's
        population size.  For example, to get a vector containing the number of people with an active infection in
        group 0 and each generation, call get_metric_in_group('I').
        '''
        if type(group_idxs) == int:
            group_idxs = [group_idxs]

        # No duplicate idxs in the group_idx list
        assert len(set(group_idxs)) == len(group_idxs)

        total_y = np.zeros(self.t + 1)
        for group in group_idxs:
            assert(group>=0)
            assert(group<self.K)

            y = self.__get_metric__(metric)[:,group]
            total_y += y

        if normalize:
            pop = 0
            for group in group_idxs:
                pop += self.S[:, group] + self.I[:, group] + self.R[:, group]  # total population by time
            total_y = total_y / pop

        if cumulative:
            return np.cumsum(total_y, axis=0)
        else:
            return total_y


    def get_metric(self, metric, aggregate=True, normalize=False, cumulative=False):
        '''
        Returns a vector where component t contains the total number of people of a particular type (S,I,R,D,H)
        in generation t.
        If aggregate is true, then this is summed across the groups.
        If normalize is true, then this is normalized to the population size.
        When normalize = True and aggregate = False, then the fraction returned is the number of people in the group
        infected divided by the size *of that group*
        For example, to get a vector containing the total number of people that were discovered each week,
        call get_metric('D'). To make it cumulative, call get_metric('D',cumulative=True)
        '''
        y = self.__get_metric__(metric)
        if normalize:
            pop = self.S + self.I + self.R  # total population in each group
            y = y / pop

        if aggregate:
            y = np.sum(y, axis=1)

        if cumulative:
            return np.cumsum(y,axis=0)
        else:
            return y

    def get_infected(self, aggregate=True, normalize=False, cumulative=False):
        return self.get_metric('I', aggregate, normalize, cumulative)

    def get_infected_for_group(self, metric, group, normalize = False, cumulative = False):
        return self.get_metric_for_group('I', group, normalize, cumulative)

    def get_total_infected_for_different_groups(self, group, normalize = False, cumulative = False):
        """
        This one also aggregates across groups
        """
        return self.get_metric_for_different_groups('I', group, normalize, cumulative).sum(axis=1)

    def get_discovered(self, aggregate=True, normalize=False, cumulative=False):
        return self.get_metric('D', aggregate, normalize, cumulative)

    def get_discovered_for_group(self, group, normalize=False, cumulative=False):
        return self.get_metric_for_group('D', group, normalize, cumulative)

    def get_total_discovered_for_different_groups(self, group, normalize = False, cumulative = False):
        """
        This one aggregates across groups
        """
        return self.get_metric_for_different_groups('D', group, normalize, cumulative).sum(axis=1)


    def get_isolated(self, group = False, iso_lengths = [8], iso_props = [1]):
        '''
        Returns the number of people in isolation during the generation.
        iso_lengths is the number days isolations lasts for each group (in ascending order)
        group is the group to look at.  If group is false, then aggregate across everyone.
        If group is specified as a list of group indices, then it aggregates across these group indices.

        iso_props is the proportion of people in each isolation length group, so
        len(iso_lengths) and len(iso_props) must be the same.

        as an intermediate step, this function calculates isolation_frac, which tells us what fraction of discovered positives
        need isolation. isolation_frac[i] is the fraction of people discovered i generations ago
        that require isolation in the current generation. For example, suppose 80% of people require isolation for
        2 generations and 20% for only 1. Then isolation_frac = [1, .2] is appropriate because all of the
        people discovered in the current generation require isolation and only 20% of those discovered in the previous
        generation still require isolation.

        Also, if the people discovered in a particular generation (say, i generations ago) only need isolation for a
        fraction of the current generation, then it is appropriate to set isolation_frac[i] to that fraction.
        For example, if isolation lasts 10 days for all individuals and the generation time is 4 days, we can set
        isolation = 3, isolation_frac = [1, 1, .5], where isolation_frac[2] = 0.5 because the positives discovered 2
        generations ago only need isolation for 10 - 2*4 = 2 days out of 4 in the current generation.

        Two more examples illustrating both of these together:

        If 80% of people require isolation for 5 days and 20% for 10 days, then set
        iso_lengths = [5,10] and iso_props = [0.8, 0.2] so that
        isolation_frac[0] = 1,
        isolation_frac[1] = 0.2*1 + 0.8*(5-4)/4 = 0.4
        isolation_frac[2] = 0.2*(10-8)/4 = 0.1

        '''
        if group == False:
            discovered = self.get_discovered()
        else:
            # Aggregates across all of the passed group indices, but not across time
            discovered = self.get_total_discovered_for_different_groups(group)

        return compute_isolated(discovered=discovered,
                                generation_time=self.generation_time,
                                iso_lengths=iso_lengths,
                                iso_props=iso_props)


    def get_generation_time(self):
        return self.generation_time

    def get_frac_susceptible(self):
        '''Returns a vector giving the fraction susceptible in each group'''
        t = self.t
        # self.S[t] / (self.S[t] + self.I[t] + self.R[t])
        return np.divide(self.S[t], (self.S[t] + self.I[t] + self.R[t]), \
                         out=np.zeros_like(self.S[t]), where=(self.S[t] + self.I[t] + self.R[t])!=0)


    def get_frac_infected(self):
        '''Returns a vector giving the fraction infected in each group'''
        t = self.t
        # self.I[t] / (self.S[t] + self.I[t] + self.R[t])
        return np.divide(self.I[t], (self.S[t] + self.I[t] + self.R[t]), \
                     out=np.zeros_like(self.S[t]), where=(self.S[t] + self.I[t] + self.R[t]) != 0)

    def get_pop_count(self):
        '''Returns the total number of people in each group'''
        t = self.t
        return self.S[t] + self.I[t] + self.R[t]