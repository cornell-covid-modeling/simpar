import numpy as np
from simpar.groups import meta_group
from simpar.sim import sim
from simpar.micro import __days_infectious_perfect_sensitivity__, days_infectious


def is_constant_population_size(s):
    """Checks that the population size of each group is contant across sim."""
    pop = s.get_metric("S") + s.get_metric("I") + s.get_metric("R")
    return all(np.isclose(pop, np.max(pop)))


def test_sim_symmetric_populations():
    """Test spread through symmetric populations is spread."""
    K = 3
    T = 20

    # symmetric populations
    pop = 100 * np.ones(K)/K
    R0 = 100 * np.array([.1, .1, .1])
    I0 = 100 * np.array([.01, .01, .01])
    S0 = pop - R0 - I0

    # Here, each group has an overall rate at which they infect others.
    # These infections are distributed proportionally to the overall population.
    # infection_rate[i,j] is the number of new infections that an infected
    # person in i creates in j.
    contact_rates = np.array([0, 1, 2])
    infection_rate = np.outer(contact_rates, pop / 100)

    s = sim(T, S0, I0, R0, infection_rate=infection_rate)
    s.step(T-1)

    assert is_constant_population_size(s)
    # S,I,R amounts for each population are initially symmetric and the new
    # infections are distributed proportionally across the populations, the
    # number infected should stay symmetric over time. That is, for each value
    # of t, y[t,0], y[t,1], and y[t,2] should be nearly identical.
    y = s.get_metric('I', aggregate=False, normalize=True)
    assert(np.isclose(y[:,0],y[:,1]).all())
    assert(np.isclose(y[:,0],y[:,2]).all())


def test_noninfectious_group():
    """Test zero cases in a non-infectious group."""
    K = 3
    T = 20

    # symmetric populations
    pop = 100 * np.ones(K)/K
    R0 = 100 * np.array([.1, .1, .1])
    I0 = 100 * np.array([0, .01, .01])
    S0 = pop - R0 - I0

    infections_per_contact = 1
    marginal_contacts = np.array([0,1,2])
    infection_rate = meta_group('Test', pop, marginal_contacts).infection_matrix(infections_per_contact)

    s = sim(T, S0, I0, R0, infection_rate=infection_rate)
    s.step(T-1)

    # The group with 0 contacts should not have any infections
    assert(np.isclose(s.get_metric_for_group('I', 0),np.zeros(T)).all())
    assert is_constant_population_size(s)


def test_sim8():
    # Scenario 1: With a meta_group
    K = 3
    T = 20

    # The populations are symmetric
    pop = 100 * np.ones(3)/3
    R0 = 100 * np.array([.1, .1, .1])
    I0 = 100 * np.array([0, .01, .01])
    S0 = pop - R0 - I0

    infections_per_contact = 1
    marginal_contacts = np.array([1,1,1])
    mg = meta_group('Test', pop, marginal_contacts)
    infection_rate = mg.infection_matrix(infections_per_contact)
    generation_time = 4/7  # in units of weeks

    s = sim(T,S0,I0,R0,infection_rate,0,0,generation_time)
    s.step(T-1)

    assert is_constant_population_size(s)

    inf_1 = s.get_metric_for_group('I', [0,1,2], normalize=True)

    # Scenario 2: No meta group
    K = 3
    T = 20

    pop = np.array([100])
    R0 = np.array([100 * 0.3])
    I0 = np.array([100 * .02])
    S0 = pop - R0 - I0

    contact_rates = np.array([1])
    infection_rate = np.outer(contact_rates,pop/100)

    generation_time = 4/7  # in units of weeks

    s = sim(T,S0,I0,R0,infection_rate,generation_time)
    s.step(T-1)

    inf_2 = s.get_metric('I', aggregate=False, normalize=True)
    assert(np.isclose(inf_1, inf_2[:,0]).all())


def test_sim_zero_prob_discvoered():
    """Test zero discovered cases when probability of discovery is zero."""
    K = 3
    T = 20

    # symmetric populations
    pop = 100 * np.ones(K)/K
    R0 = 100 * np.array([.1, .1, .1])
    I0 = 100 * np.array([0, .01, .01])
    S0 = pop - R0 - I0

    infections_per_contact = 1
    marginal_contacts = np.array([0,1,2])
    infection_rate = meta_group("UG", pop, marginal_contacts).infection_matrix(infections_per_contact)
    generation_time = 4/7  # in units of weeks

    s = sim(T, S0, I0, R0, infection_rate=infection_rate,
            generation_time=generation_time, infection_discovery_frac=0,
            recovered_discovery_frac=0)
    s.step(T-1)

    assert is_constant_population_size(s)
    # Since no one is discovered, the number discovered should be 0
    discovered = s.get_discovered(cumulative=True)
    assert(np.isclose(discovered, np.zeros(T)).all())


# TODO (hwr): Leaving a note here that test_sim3 containted unused analysis
# but was not a test. Hence, it was removed on 2021-12-28. Notes given below.

# Calculate the probability of infection.
# A ballpark estimate is that R0 with 1x / wk testing and a 2-day delay from
# sampling to isolation is 5, with a 4 day generation time.  We think that
# this outbreak was driven by the people with 6 contacts per period above
# because the sum of their proportions of the UG population is about 1900
# people. To achieve this, we set infections_per_contact = 5/6 so that the
# number of secondary infections from someone with 6 contacts is 5. We then
# adjust this by multiplying by the number of days infectious under our
# testing strategy, divided by the number under our December Omicron outbreak.
