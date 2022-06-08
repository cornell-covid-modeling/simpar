"""Heterogeneous population manager.

This module defines a [MetaGroup] class which describes a group of people
for which most parameters are similar but who have varying degrees of social
contact. Furthermore, it defines a [Population] which is comprised of multiple
[MetaGroup]s. Testing strategies can be set at granularity of [MetaGroup]s.
"""

__author__ = "Sam Stan (samstan) and Xiangyu Zhang (xiangyu-zhang-95)"


from typing import Dict
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

    @staticmethod
    def from_truncated_pareto(name: str, population: float, a: float, ub: int):
        """Initialize a meta-group from a truncated Pareto distribution.

        Args:
            name (str): Name of the metagroup.
            population (float): Total population in this metagroup.
            a (float): Shape parameter (alpha) for the Pareto distribution.
            ub (int): Truncation point for the Pareto distribution.
        """
        pop_frac = np.array([pareto.pdf(k,a) for k in range(1, ub+1)])
        pop_frac = pop_frac / np.sum(pop_frac)  # normalize
        pop = population * pop_frac
        contact_units = np.arange(1, len(pop) + 1)
        return MetaGroup(name, pop, contact_units)

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

    def __init__(self, meta_groups_dict: Dict[str, MetaGroup],
                 meta_group_contact_matrix: np.ndarray):
        """
        Initialize a population.

        A population is defined by a dictionary of meta-groups:
        [meta_groups_dict]. Meta-group interactions are not assumed to be
        well-mixed. The matrix [meta_group_contact_matrix] indicates how
        metagroups interact with one another. This is encoded in the
        [infection_matrix] which is normalized to be in "contact units."

        Args:
            meta_groups_dict (Dict[str, MetaGroup]): Dictionary of meta-groups.
            meta_group_contact_matrix (np.ndarray): Interactions between \
                meta-groups where entry (i,j) is the conditional probability \
                that the exposed is in meta-group j, given that the source is \
                in meta-group i.
        """
        self.meta_groups_dict = meta_groups_dict
        self.meta_group_names = list(self.meta_groups_dict.keys())
        self.meta_group_list = list(self.meta_groups_dict.values())
        self.meta_group_contact_matrix = meta_group_contact_matrix

        cum_tot = np.cumsum([mg.K for _, mg in meta_groups_dict.items()])

        self._meta_group2idx = {}
        for i, (name, mg) in enumerate(meta_groups_dict.items()):
            self._meta_group2idx[name] = \
                list(range(cum_tot[i] - mg.K, cum_tot[i]))

    @staticmethod
    def from_truncated_paretos_dictionary(d: Dict):
        """Return a [Population] initialized from the given dictionary."""
        meta_groups = {}
        for key in d["meta_groups"]:
            name = d["meta_group_names"][key]
            pop = d["population_counts"][key]
            a = d["pop_pareto_shapes"][key]
            ub = d["pop_pareto_ubs"][key]
            meta_group = MetaGroup.from_truncated_pareto(name, pop, a, ub)
            meta_groups[key] = meta_group

        meta_group_contact_matrix = np.array(d["meta_group_contact_matrix"])

        return Population(meta_groups, meta_group_contact_matrix)

    def meta_group_ids(self, meta_group):
        """Return the group ids of the groups in the given meta-group."""
        return self._meta_group2idx[meta_group]

    def infection_matrix(self, infections_per_contact_unit: float):
        """Return the infection matrix."""
        Ks = [mg.K for mg in self.meta_group_list]
        dim_tot = np.sum(Ks)
        cum_tot = np.hstack((0, np.cumsum(Ks)))

        res = np.zeros((dim_tot, dim_tot))
        for a, source in enumerate(self.meta_group_list):
            for b, exposed in enumerate(self.meta_group_list):
                for i in range(source.K):
                    for j in range(exposed.K):
                        q = exposed.pop[j] * exposed.contact_units[j] / \
                            np.sum(exposed.pop * exposed.contact_units)
                        res[cum_tot[a]+i, cum_tot[b]+j] = \
                            source.contact_units[i] * \
                            infections_per_contact_unit[a] * \
                            self.meta_group_contact_matrix[a,b] * q

        return res

    def infection_discovery_frac(self, infection_discovery_frac):
        """Return the fraction of infections that are discovered."""
        res = []
        for i, mg in enumerate(self.meta_group_list):
            for _ in range(mg.K):
                res.append(infection_discovery_frac[i])
        return np.array(res)

    def recovered_discovery_frac(self, recovered_discovery_frac):
        """Return the fraction of recovered that are discovered."""
        res = []
        for i, mg in enumerate(self.meta_group_list):
            for _ in range(mg.K):
                res.append(recovered_discovery_frac[i])
        return np.array(res)

    def outside_rate(self, outside_rates: np.ndarray):
        """Return the outside rate."""
        Ks = [mg.K for mg in self.meta_group_list]
        dim_tot = np.sum(Ks)
        cum_tot = np.hstack((0, np.cumsum(Ks)))

        res = np.zeros(dim_tot)
        for i, meta_group in enumerate(self.meta_group_list):
            for j in range(self.meta_group_list[i].K):
                q = meta_group.pop[j] / np.sum(meta_group.pop)
                res[cum_tot[i]+j] = outside_rates[i] * q

        return res

    def get_init_SIR(self, init_infections: np.ndarray,
                     init_recovered: np.ndarray, weight: str = "population"):
        """Return initial SIR vectors.

        Given [init_infections] and [init_recovered] at the meta-group level,
        the [weight] parameter specifies how these counts should be distributed
        across the groups within each metagroup. The available options for
        [weight] are:

        - "population": Each person is equally likely to be infected.
        - "population x contacts": A person's probability of being infected is
          proportional to their amount of contact.
        - "most social": The initial infections are in the most social group.

        Args:
            init_infections (np.ndarray): Initial infections per meta-group.
            init_recovered (np.ndarray): Initial recovered per meta-group.
            weight (str): {population, population x contacts, most_social}
        """
        SIR = [[],[],[]]
        for i in range(len(self.meta_group_list)):
            group = self.meta_group_list[i]
            S0, I0, R0 = group.get_init_SIR(init_infections[i],
                                            init_recovered[i],
                                            weight=weight)
            SIR[0] += list(S0)
            SIR[1] += list(I0)
            SIR[2] += list(R0)

        SIR = np.array(SIR)
        return SIR[0], SIR[1], SIR[2]
