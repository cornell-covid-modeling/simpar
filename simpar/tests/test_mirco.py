import pytest
import numpy as np
from simpar.micro import days_infectious, days_infectious_perfect_sensitivity


@pytest.mark.parametrize("T,D,f,R,I",[
    (np.inf, 2, 0.5, 5, 5),
    (np.inf, 2, 0.7, 5, 5),
    (np.inf, 2, 0.5, 3, 3),
    (3, np.inf, 0.6, 5, 5),
    (5, np.inf, 0.9, 1, 1)])
def test_no_surveillance_test(T,D,f,R,I):
    assert days_infectious(T, D, f, R) == I
    assert days_infectious_perfect_sensitivity(T, D, R) == I


@pytest.mark.parametrize("T,D,R",[
    (5, 2, 10),
    (3, 2, 10),
    (5, 3, 7),
    (5, 3, 10)])
def test_perfect_sensitivity(T,D,R):
    x1 = days_infectious(T, D, 1, R)
    x2 = days_infectious_perfect_sensitivity(T, D, R)
    assert x1 == x2


@pytest.mark.parametrize("T,D,f,R",[
    (5, 2, 0.5, 10),
    (5, 2, 0.5, 10),
    (5, 3, 0.8, 10),
    (5, 3, 0.8, 10)])
def test_more_delay(T,D,f,R):
    assert days_infectious(T, D, f, R) < days_infectious(T, D+1, f, R)


@pytest.mark.parametrize("T,D,f,R",[
    (5, 2, 0.5, 10),
    (5, 2, 0.5, 10),
    (5, 3, 0.8, 10),
    (5, 3, 0.8, 10)])
def test_more_sensitivity(T,D,f,R):
    assert days_infectious(T, D, f+0.2, R) < days_infectious(T, D, f, R)


@pytest.mark.parametrize("T,D,f,R",[
    (5, 2, 0.5, 10),
    (5, 2, 0.5, 12),
    (5, 3, 0.8, 8),
    (5, 3, 0.8, 6)])
def test_shorter_max_infectious_days(T,D,f,R):
    assert days_infectious(T, D, f, R) < days_infectious(T, D, f, R+3)


@pytest.mark.parametrize("T,D,R",[
    (5, 2, 10),
    (5, 2, 12),
    (5, 3, 8),
    (5, 3, 6)])
def test_zero_sensitivity(T,D,R):
    assert days_infectious(T, D, 0, R) == days_infectious(np.inf, D, 0, R)
