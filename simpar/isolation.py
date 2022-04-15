import numpy as np
from typing import List


def compute_isolated(discovered: np.ndarray,
                     generation_time: float,
                     iso_lengths: List[int],
                     iso_props: List[int]
                     ) -> np.ndarray:
    """Return the isolated count over time given the discovered count over time

    As an intermediate step, this function calculates isolation_frac, which
    tells us what fraction of discovered positives need isolation.
    isolation_frac[i] is the fraction of people discovered i generations ago
    that require isolation in the current generation. For example, suppose 80%
    of people require isolation for 2 generations and 20% for only 1. Then
    isolation_frac = [1, .2] is appropriate because all of the people
    discovered in the current generation require isolation and only 20% of
    those discovered in the previous generation still require isolation.

    As another example:
    If 80% of people require isolation for 5 days and 20% for 10 days, then set
    iso_lengths = [5,10] and iso_props = [0.8, 0.2] so that
    isolation_frac[0] = 1,
    isolation_frac[1] = 0.2*1 + 0.8*(5-4)/4 = 0.4
    isolation_frac[2] = 0.2*(10-8)/4 = 0.1

    Args:
        discovered (np.ndarray): Discovered vector. Note that this vector is \
            expected to be flattened with respect to metagroups.
        generation_time (float): The number of days per generation.
        iso_lengths (List[int]): List of isolation lengths (in days).
        iso_props (List[int])): List of probability of isolation lengths.
    """
    iso_len = int(np.ceil(iso_lengths[-1]/generation_time))

    def cut01(s):
        if s < 0:
            return 0
        elif s > 1:
            return 1
        else:
            return s

    isolation_frac = np.ones(iso_len)
    for i in range(1,iso_len):
        isolation_frac[i] = 0
        for j in range(len(iso_lengths)):
            isolation_frac[i] += \
                iso_props[j] * cut01((iso_lengths[j] - generation_time*i) / generation_time)

    isolated = np.zeros(len(discovered))
    for t in range(len(discovered)):
        for i in range(iso_len):
            if t-i >= 0:
                # Add in the people who were discovered i generations ago
                isolated[t] = isolated[t] + isolation_frac[i] * discovered[t-i]

    return isolated
