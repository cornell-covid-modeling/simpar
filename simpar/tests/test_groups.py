import numpy as np
from simpar.groups import MetaGroup
from simpar.sim import Sim


def validate(sim):
    pop = np.sum(sim.S, axis=1) + np.sum(sim.I, axis=1) + np.sum(sim.R, axis=1)
    assert all(np.isclose(pop, np.max(pop)))
    assert np.isclose(sim.D + sim.H, sim.R + sim.I).all()


def test_sim8():
    # Scenario 1: With a MetaGroup
    K = 3
    T = 20

    # The populations are symmetric
    pop = 100 * np.ones(K)/K
    R0 = 100 * np.array([.1, .1, .1])
    I0 = 100 * np.array([0, .01, .01])
    S0 = pop - R0 - I0

    infections_per_contact = 1
    marginal_contacts = np.array([1,1,1])
    mg = MetaGroup('Test', pop, marginal_contacts)
    infection_rate = mg.infection_matrix(infections_per_contact)

    sim = Sim(T,S0,I0,R0,infection_rate,0,0)
    sim.step(T-1)

    validate(sim)

    inf_1 = sim.I

    # Scenario 2: No meta group
    K = 3
    T = 20

    pop = np.array([100])
    R0 = np.array([100 * 0.3])
    I0 = np.array([100 * .02])
    S0 = pop - R0 - I0

    contact_rates = np.array([1])
    infection_rate = np.outer(contact_rates,pop/100)

    s = Sim(T,S0,I0,R0,infection_rate)
    s.step(T-1)

    inf_2 = sim.I
    assert(np.isclose(inf_1, inf_2).all())
