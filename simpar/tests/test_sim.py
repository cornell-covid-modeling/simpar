import os
import yaml
import pytest
import numpy as np
from simpar.sim import Sim


def sim_from(dictionary):
    T = dictionary["T"]
    S0 = np.array(dictionary["S0"])
    I0 = np.array(dictionary["I0"])
    R0 = np.array(dictionary["R0"])
    infection_rate = np.array(dictionary["infection_rate"])
    infection_discovery_frac = np.array(dictionary["infection_discovery_frac"])
    recovered_discovery_frac = np.array(dictionary["recovered_discovery_frac"])
    outside_rate = np.array(dictionary["outside_rate"])
    return Sim(max_T=T, init_susceptible=S0, init_infected=I0,
               init_recovered=R0, infection_rate=infection_rate,
               infection_discovery_frac=infection_discovery_frac,
               recovered_discovery_frac=recovered_discovery_frac,
               outside_rate=outside_rate)


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')
with open(os.path.join(RESOURCES_PATH, "test_sim.yaml"), "r") as f:
    sims = yaml.safe_load(f)
    SIMULATIONS = {k: sim_from(v) for k,v in sims.items()}
    # run all simulations to completion
    for _, v in SIMULATIONS.items():
        v.step(v.max_T - 1)


@pytest.mark.parametrize("name, sim", SIMULATIONS.items())
def test_constant_population(name, sim):
    """Test that S+I+R is constant across the simulation."""
    pop = np.sum(sim.S + sim.I + sim.R, axis=1)
    assert all(np.isclose(pop, pop[0]))


@pytest.mark.parametrize("name, sim", SIMULATIONS.items())
def test_IR_is_DH(name, sim):
    """Test that I+R = D+H across the simulation."""
    assert np.isclose(sim.D + sim.H, sim.R + sim.I).all()


@pytest.mark.parametrize("name, sim", SIMULATIONS.items())
def test_susceptible_limits_infection(name, sim):
    """Test that infections is no more than susceptible from last period."""
    for t in range(sim.max_T - 2):
        assert np.sum(sim.I[t+1]) <= np.sum(sim.S[t])


def test_sim_symmetric_populations():
    """Test spread through symmetric populations."""
    sim = SIMULATIONS["three_groups_symmetric_pop"]
    # S,I,R amounts for each population are initially symmetric and the new
    # infections are distributed proportionally across the populations. The
    # number infected should stay symmetric over time.
    assert np.isclose(sim.I[:,0], sim.I[:,1]).all()
    assert np.isclose(sim.I[:,0], sim.I[:,2]).all()


def test_noninfectious_group():
    """Test zero cases in a non-infectious group."""
    sim = SIMULATIONS["noninfectious_group"]
    # The group with 0 contacts should not have any infections
    assert np.isclose(sim.I[:,0], np.zeros(sim.max_T)).all()


def test_zero_prob_discovered():
    """Test zero discovered cases when probability of discovery is zero."""
    sim = SIMULATIONS["no_discovery"]
    assert np.isclose(np.sum(sim.D, axis=1), np.zeros(sim.max_T)).all()


def test_perfect_sensitivity():
    """Test no hidden cases when probability of discovery is 1."""
    sim = SIMULATIONS["perfect_sensitivity"]
    assert np.isclose(np.sum(sim.H, axis=1), np.zeros(sim.max_T)).all()
