import numpy as np
from simpar.sim import Sim


def validate(sim):
    pop = np.sum(sim.S, axis=1) + np.sum(sim.I, axis=1) + np.sum(sim.R, axis=1)
    assert all(np.isclose(pop, np.max(pop)))
    assert np.isclose(sim.D + sim.H, sim.R + sim.I).all()


def test_sim_symmetric_populations():
    """Test spread through symmetric populations."""
    K = 3
    T = 20

    # symmetric populations
    pop = 100 * np.ones(K) / K
    R0 = 100 * np.array([.1, .1, .1])
    I0 = 100 * np.array([.01, .01, .01])
    S0 = pop - R0 - I0

    # Here, each group has an overall rate at which they infect others.
    # These infections are distributed proportionally to overall population.
    # infection_rate[i,j] is the number of new infections that an infected
    # person in i creates in j.
    contact_rates = np.array([0, 1, 2])
    infection_rate = np.outer(contact_rates, pop / 100)

    sim = Sim(T, S0, I0, R0, infection_rate=infection_rate)
    sim.step(T-1)

    validate(sim)
    # S,I,R amounts for each population are initially symmetric and the new
    # infections are distributed proportionally across the populations, the
    # number infected should stay symmetric over time. That is, for each value
    # of t, y[t,0], y[t,1], and y[t,2] should be nearly identical.
    y = sim.I
    assert(np.isclose(y[:,0], y[:,1]).all())
    assert(np.isclose(y[:,0], y[:,2]).all())


def test_noninfectious_group():
    """Test zero cases in a non-infectious group."""
    K = 3
    T = 20

    # symmetric populations
    pop = 100 * np.ones(K)/K
    R0 = 100 * np.array([.1, .1, .1])
    I0 = 100 * np.array([0, .01, .01])
    S0 = pop - R0 - I0

    infection_rate = np.array([[0.0, 0.2, 0.3],
                               [0.0, 0.7, 0.4],
                               [0.0, 0.4, 0.9]])

    sim = Sim(T, S0, I0, R0, infection_rate=infection_rate)
    sim.step(T-1)

    # The group with 0 contacts should not have any infections
    assert(np.isclose(sim.I[:,0], np.zeros(T)).all())
    validate(sim)


def test_sim_zero_prob_discovered():
    """Test zero discovered cases when probability of discovery is zero."""
    K = 3
    T = 20

    # symmetric populations
    pop = 100 * np.ones(K)/K
    R0 = 100 * np.array([0, 0, 0])
    I0 = 100 * np.array([0, .01, .01])
    S0 = pop - R0 - I0

    infection_rate = np.array([[0.0, 0.2, 0.3],
                               [0.0, 0.7, 0.4],
                               [0.0, 0.4, 0.9]])

    sim = Sim(T, S0, I0, R0, infection_rate=infection_rate,
              infection_discovery_frac=0,
              recovered_discovery_frac=0)
    sim.step(T-1)

    validate(sim)
    # Since no one is discovered, the number discovered should be 0
    discovered = np.sum(sim.D, axis=1)
    assert np.isclose(discovered, np.zeros(T)).all()
