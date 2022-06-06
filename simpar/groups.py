"""Heterogeneous population manager.

This module defines a [MetaGroup] class which describes a group of people
for which most parameters are similar but who have varying degrees of social
contact. Furthermore, it defines a [Population] which is comprised of multiple
[MetaGroup]s. Testing strategies can be set at granularity of [MetaGroup]s.
"""

__author__ = "Sam Stan (samstan) and Xiangyu Zhang (xiangyu-zhang-95)"


from typing import List
import numpy as np
from scipy.stats import pareto


class MetaGroup:
    """
    Initialize a meta-group.

    A "meta-group" is a collection of groups. Each group within the meta-group
    is associated with a level of social contact.

    The population is assumed to be well-mixed meaning that group i's
    amount of interaction with group j is proportional to group j's fraction
    of the population and both groups contact levels.

    In a school setting, example meta-groups could be undergraduates,
    professional students, graduate students, and faculty/staff.
    """
    def __init__(self, name, pop, contact_units):
        assert (len(pop) == len(contact_units))
        self.name = name
        self.contact_units = contact_units
        self.K = len(contact_units)
        self.pop = pop

    @property
    def name(self):
        """Return the name of this meta-group."""
        return self.name

    @property
    def K(self):
        """Return the number of contact levels (groups) in this meta-group."""
        return self.K

    @property
    def contact_units(self):
        """Return the contact_units in this meta-group."""
        return self.contact_units

    @property
    def pop(self):
        """Return the distribution of the population across contact levels."""
        return self.pop

    def infection_matrix(self, infections_per_contact_unit: float):
        """Return the infection matrix."""
        # Infection matrix among these groups assumes population is well-mixed.
        marginal_contact = self.pop * self.contact_units / \
            np.sum(self.pop * self.contact_units)
        return infections_per_contact_unit * \
            np.outer(self.contact_units, marginal_contact)

    def outside_rate(self, outside_rate: float):
        """Return the outside rate."""
        # Outside rate assumes well-mixed with external population
        return outside_rate * (self.pop * self.contact_units /
                               np.sum(self.pop * self.contact_units))

    def get_init_SIR(self, init_infections: float, init_recovered: float,
                     weight: str = "population"):
        """Return initial SIR vectors.

        Given [init_infections] and [init_recovered] aggregated at the
        meta-group level, the [weight] parameter specifies how these counts
        should be distributed across the groups within this metagroup. The
        available options for [weight] are:

        - "population": Each person is equally likely to be infected.
        - "population x contacts": A person's probability of being infected is
          proportional to their amount of contact.
        - "most social": The initial infections are in the most social group.

        Args:
            init_infections (float): Initial infections count in meta-group.
            init_recovered (float): Initial recovered count in meta-group.
            weight (str): {population, population x contacts, most_social}
        """
        if weight == "population":
            w = self.pop
        elif weight == "population x contacts":
            w = self.contact_units * self.pop
        elif weight == "most_social":
            w = np.zeros(self.K)
            w[-1] = 1
        else:
            raise ValueError("The provided weight is not supported.")
        w = w / np.sum(w)  # normalize
        R0 = init_recovered * w
        I0 = init_infections * w
        S0 = np.maximum(self.pop - R0 - I0, 0)
        return S0, I0, R0


class Population:
    """
    A population is a collection of meta-groups.
    """

    def __init__(self, meta_group_list: List[MetaGroup],
                 meta_group_contact_matrix: np.ndarray):
        """
        Initialize a population.

        A population is defined by a list of meta-groups: [meta_group_list].
        Meta-group interactions are not assumed to be well-mixed. The matrix
        [meta_group_contact_matrix] indicates how metagroups interact with
        one another. This is encoded in the [infection_matrix] which is
        normalized to be in "contact units."

        Args:
            meta_group_list (List[MetaGroup]): List of meta-groups.
            meta_group_contact_matrix (np.ndarray): Interactions between \
                meta-groups where entry (i,j) is the conditional probability \
                that the exposed is in meta-group j, given that the source is \
                in meta-group i.
        """
        self.meta_group_list = meta_group_list
        self.meta_group_names = [mg.name for mg in meta_group_list]
        self.meta_group_contact_matrix = meta_group_contact_matrix

        cum_tot = np.cumsum(mg.K for mg in meta_group_list)
        self._meta_group2idx = {}
        for i, mg in enumerate(meta_group_list):
            self._meta_group2idx[mg] = \
                list(range(cum_tot[i] - mg.K, cum_tot[i]))

    @staticmethod
    def from_scenario(scenario):
        """Initialize a population from the parameters in a scenario."""
        population_count = scenario["population_count"]
        meta_groups = []
        for meta_group in scenario["metagroups"]:
            name = meta_group
            b = scenario['pop_fracs_pareto'][meta_group]
            n = scenario['pop_fracs_max'][meta_group]
            pop_frac = np.array([pareto.pdf(k,b) for k in range(1, n+1)])
            pop_frac = pop_frac / np.sum(pop_frac)
            pop = population_count[meta_group] * pop_frac
            contact_units = np.arange(1, len(pop) + 1)
            meta_groups.append(MetaGroup(name, pop, contact_units))
        return Population(meta_groups, np.array(scenario['meta_matrix']))

    @property
    def meta_group_names(self):
        """Return the names of the meta-groups in this population."""
        return self.meta_group_names

    def meta_group_ids(self, meta_group):
        """Return the group ids of the groups in the given meta-group."""
        return self._meta_group2idx[meta_group]

    def infection_matrix(self, infections_per_contact_unit: float):
        """Return the infection matrix."""
        Ks = [mg.K for mg in self.meta_group_list]
        dim_tot = np.sum(Ks)
        cum_tot = np.cumsum(Ks)

        res = np.zeros((dim_tot, dim_tot))
        for a, source in enumerate(self.meta_group_list):
            for b, exposed in enumerate(self.meta_group_list):
                for i in range(source.K):
                    for j in range(exposed.K):
                        q = exposed.pop[j] * exposed.contact_units[j] / \
                            np.sum(exposed.pop * exposed.contact_units)
                        res[cum_tot[a]+i, cum_tot[b]+j] = \
                            source.contact_units[j] * \
                            self.meta_group_contact_matrix[a,b] * q

        return infections_per_contact_unit * res

    def outside_rate(self, outside_rates: np.ndarray):
        """Return the outside rate."""
        Ks = [mg.K for mg in self.meta_group_list]
        dim_tot = np.sum(Ks)
        cum_tot = np.cumsum(Ks)

        res = np.zeros(dim_tot)
        for i, meta_group in enumerate(self.meta_group_list):
            for j in range(self.meta_group_list[i].K):
                q = meta_group.pop[j] / np.sum(meta_group.pop)
                res[cum_tot[i]+j] = outside_rates[i] * q

        return res

    def get_init_SIR(self, init_infections: float, init_recovered: float,
                     weight: str = "population"):
        """Return initial SIR vectors.

        Given [init_infections] and [init_recovered] aggregated at the
        population level, assume that both are distributed across meta-groups
        proportional to the population.

        The [weight] parameter specifies how these counts should be distributed
        across the groups within each metagroup. The available options for
        [weight] are:

        - "population": Each person is equally likely to be infected.
        - "population x contacts": A person's probability of being infected is
          proportional to their amount of contact.
        - "most social": The initial infections are in the most social group.

        Args:
            init_infections (float): Initial infections count in population.
            init_recovered (float): Initial recovered count in population.
            weight (str): {population, population x contacts, most_social}
        """
        meta_group_pops = np.array([sum(g.pop) for g in self.meta_group_list])
        meta_group_prop = meta_group_pops / sum(meta_group_pops)
        init_infections = init_infections * meta_group_prop
        init_recovered = init_recovered * meta_group_prop

        return self._get_init_SIR_vec(init_infections, init_recovered, weight)

    def _get_init_SIR_vec(self, init_infections: np.ndarray,
                          init_recovered: np.ndarray,
                          weight: str = "population"):
        SIR = []
        for i in range(len(self.meta_group_list)):
            group = self.meta_group_list[i]
            S0, I0, R0 = group.get_init_SIR(init_infections[i],
                                            init_recovered[i],
                                            weight=weight)
            SIR.append([S0, I0, R0])
        SIR = np.array(SIR)

        S0 = SIR[:,0].flatten()
        I0 = SIR[:,1].flatten()
        R0 = SIR[:,2].flatten()
        return S0, I0, R0
