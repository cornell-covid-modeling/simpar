"""Methods to perform "microscopic" calculations that predict days infectious.

.. code-block:: text

    T | time between surveillance tests
    X | beginning of period when an individual is infectious (and detectable)
    D | delay to isolate after testing positive
    R | total length of the infectious period
    N | index of first surveillance to test
    I | total time an individual is infectious AND free

    ========================================
    Example timeline:
    Individual tests positive on second test

    |---|------|-----|----|-----|----|----|
    0   X      T    T+D   2T    I    3T   R

    N          0          1          2
    ========================================

We will use the above notation to discuss the calculations performed in
this module. The infection begins between two surveillance tests at some
point X which is uniformly distributed on [0,T]. Hence, the number of days
between infection and the first surveillance test is T-X.

Note: We (pessimistically) assume a person is infectious the entire time they
are PCR-detectable and that the infection level remains constant.

Using this notation, the number of days when the person is infectious is
I = min(T-X+NT+D, R) where the first case represents isolating the individual
before the end of their infectious period.
"""

__author__ = "Peter Frazier (peter-i-frazier)"

import numpy as np


def _conditional_days_infectious(n: int, days_between_tests: float,
                                 isolation_delay: float,
                                 max_infectious_days: float):
    """
    Compute E[I | the nth surveillance test is first to test positive].

    E[I | the nth surveillance test is first to test positive]
    = min(T-X+nT+D, R)
    = nT + D + min(T-X, R-D-nT)
    = nT + D + T * min((T-X)/T, (R-D-nT)/T)

    Note U = (T-X)/T is uniformly distributed between 0 and 1.
    Let b = (R-D-NT)/T. Let's compute y = E[min(U,b)].

    If b <= 0,     y = b
    If b > 1,      y = 1/2
    If b in (0,1), y = b*(1-b/2)

    So the conditional expected time is we'll return D + nT + T * y
    """
    T = days_between_tests
    D = isolation_delay
    R = max_infectious_days

    assert T > 0

    if T == np.inf:
        return max_infectious_days

    b = (R - D - n*T) / T
    if b < 0:
        y = 0
    elif b > 1:
        y = 0.5
    else:
        y = b * (1 - 0.5 * b)

    return D + (n * T) + T * y


def days_infectious(days_between_tests: float, isolation_delay: float,
                    sensitivity: float, max_infectious_days: float):
    """Return the expected time someone is infectious and free.

    Equivalently, Compute E[I]. Note that the number of surveillance tests N
    that are required for a person to test positive is a geometric random
    variable with probability given by [sensitivity]. So the person tests
    positive on test n (where the first test is n=0) with probability
    P(N=n) = [sensitivity] * np.pow(1-[sensitivity], n).

    Args:
        days_between_tests (float): Number of days between surveillance \
            tests. Provide np.inf for no surveillance testing.
        isolation_delay (float): Number of days to isolate after positive test.
        sensitivity (float): Sensitivity of surveillance test.
        max_infectious_days (float): Maximum infectious period.
    """
    T = days_between_tests
    D = isolation_delay
    R = max_infectious_days

    if T == np.inf or D == np.inf:
        return max_infectious_days

    n = 0
    prob = 1  # contains Prob(N>=n)
    y = 0  # sum of Prob(N=n') * E[days_infectious | N=n'] over 0 <= n' < n
    while D + (n*T) < R:
        pn = sensitivity * np.power(1-sensitivity,n)  # Prob(N=n)
        y = y + pn * _conditional_days_infectious(n, days_between_tests,
                                                  isolation_delay,
                                                  max_infectious_days)
        prob = prob - pn
        n = n+1
    # Since X <= T, once D + nT >= R, we have that
    # days_infectious = min(D + nT + T - X, R) = R. This will remain true if n
    # increases. Thus, E[days_infectious | N=n] = R for this n and larger.
    # Thus, the sum of Prob(N=n') * E[days_infectious | N=n'] for n' >= n is
    # Prob(N>=n) * R
    y = y + prob*R

    return y


def days_infectious_perfect_sensitivity(days_between_tests: float,
                                        isolation_delay: float,
                                        max_infectious_days: float):
    """Return the expected time someone is infectious and free assuming
    perfect test sensitivity."""
    T = days_between_tests
    D = isolation_delay
    R = max_infectious_days

    assert T > 0

    if T == np.inf or D == np.inf:
        return max_infectious_days

    b = (R - D) / T
    if b < 0:
        y = 0
    elif b > 1:
        y = 0.5
    else:
        y = b * (1 - 0.5 * b)

    return D + T * y
