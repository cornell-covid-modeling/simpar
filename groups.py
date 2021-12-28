from typing import List
import numpy as np
'''
This module contains code for working with groups and meta-groups
'''

class meta_group:
    '''
    A "meta-group" is a collection of groups.
    Each group within the meta-group is associated with a level of contact.

    Given that a contact exposes a member of a meta-group, the probability that the person exposed is within group i
    is proportional to the population of group i times group i's level of contact.

    Examples of meta-groups: UG, Grad-Professional, Staff/Faculty, Grad-Research
    '''
    def __init__(self, name, pop, contact_units):
        assert (len(pop) == len(contact_units))
        self.name = name # Name of the meta-group, e.g., "UG"
        self.contact_units = contact_units # Amount of contact that each group has
        self.K = len(contact_units) # Number of groups
        self.pop = pop # Number of people in each group

    # used to be called well_mixed_infection_rate(pop, marginal_contacts, infections_per_contact)
    def infection_matrix(self, infections_per_contact_unit):
        '''
        Returns an infection rate matrix that corresponds to well-mixed interactions within the meta-group.

        The matrix returned has entry [i,j] equal to the total number of secondary infections expected in
        group j that result from a single infection in group i, assuming that each contact_unit results in
        infections_per_contact_unit total secondary infections.

        A person in group i has an amount of contact during their infectious period (summed over all exposed groups)
        equal to self.contact_units[i].

        The units in "contact units" can be total contacts over the course of someone's infectious period,
        in which case infections_per_contact is the same as the probability of transmission given contact.
        It could also be the *rate* at which people have contact per day, in which case infections_per_contact
        should be the probability of transmission given contact times the expected length of a person's
        infectious period.
        '''

        # An incoming contact lands in a population with a probability proportional to its number of outgoing contacts,
        # which is pop[i]*self.contact_units[i].
        q = self.pop * self.contact_units / np.sum(self.pop * self.contact_units)

        # The total number of people infected by a positive in group i is infections_per_contact * marginal_contacts[i]
        r = infections_per_contact_unit * self.contact_units

        # When a person in group i is infected, the number of people infected in group j is then r[i]*q[j]
        infection_rates = np.outer(r, q)
        return infection_rates


class population:
    '''
    A population is a collection of meta-groups
    '''

    def __init__(self, meta_group_list: List[meta_group], meta_group_contact_matrix: np.ndarray):
        '''
        meta_group_matrix[i,j] is a matrix that gives the number of contacts that occurred where the source case was
        in meta-group i and the exposed group was in meta-group j.

        We normalize each row so that it sums to 1, so that meta_group[i,j] is the conditional probability that
        the exposed is in meta-group j, given that the source is in meta-group i.  Note that these conditional
        probabilities may be influenced by the population sizes -- if meta-group j is bigger, then it may be more
        likely to be the exposed meta-group.
        '''
        self.meta_group_contact_matrix = meta_group_contact_matrix
        self.meta_group_list = meta_group_list

        n, m = len(meta_group_contact_matrix), len(meta_group_contact_matrix[0])
        assert (n == m)

        k = len(meta_group_list)
        assert (k == n)

    def infection_matrix(self, infections_per_contact_unit):
        '''
        Returns an infection rate matrix that corresponds to well-mixed interactions within each meta-group,
        and interactions across meta-groups given by self.meta_group_contact_matrix.

        The matrix returned has entry [i,j] equal to the total number of secondary infections expected in
        group j that result from a single infection in group i, assuming that each contact_unit results in
        infections_per_contact_unit total secondary infections.


        Here, a "group" is an integer that corresponds to a meta-group and a group within that meta-group.
        '''

    def idx_to_groupname(self, i):
        '''
        Returns a string naming the group indexed by i, e.g., "UG 6".

        The name is a concatenation of the group's meta-group name and the group's number of contact units
        '''

    def metagroup_indices(self, meta_group):
        '''
        Returns a list of group indices corresponding to the passed meta-group name
        '''
        

    def groupname_to_idx(self, groupname):
        '''
        Returns the group index associated with a groupname
        '''



### OLD CODE

def well_mixed_infection_rate_multiple_meta_groups(pop, marginal_contacts, infections_per_contact):
    '''
    marginal_contacts is a dictionary of histograms, e.g., where
    { 'UG': [.1, .2, .3 ], 'Grad/Professional' : [.2, .1, .3] }

    '''

'''
Returns an infection rate matrix that corresponds to well-mixed interactions between groups, where each group has a
amount of contact during their infectious period (summed over all exposed groups) given by the vector
marginal_contacts and a population size by the vector pop.  The number of infections per unit of contact in
marginal_contact (infections_per_contact) is a scalar and applies to all contacts. The units of "marginal_contacts"
could be total contacts over the course of someone's infectious period, in which case infections_per_contact is the
same as the probability of transmission given contact.  It could also be the *rate* at which people have contact per
day, in which case infections_per_contact should be the probability of transmission given contact times the expected
length of a person's infectious period.
'''
def well_mixed_infection_rate_one_meta_group(pop, marginal_contacts, infections_per_contact):
    assert (len(pop) == len(marginal_contacts))
    frac_pop = pop / np.sum(pop)  # convert to a fraction
    K = len(marginal_contacts)

    # An incoming contact lands in a population with a probability proportional to its number of outgoing contacts,
    # which is q[i] = frac_pop[i]*marginal_contacts[i].
    q = frac_pop * marginal_contacts / np.sum(frac_pop * marginal_contacts)

    # The total number of people infected by a positive in group i is infections_per_contact * marginal_contacts[i]
    r = infections_per_contact * marginal_contacts

    # When a person in group i is infected, the number of people infected in group j is then r[i]*q[j]

    infection_rates = np.outer(r, q)
    return infection_rates