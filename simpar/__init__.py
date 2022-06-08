"""
simpar
======

simpar simulates a pandemic's spread through a population using an SIR model.
It provides the ability to manage a heterogeneous population with varying
contact levels. The tool focuses on providing functionality for assessing
various pandemic response strategies such as isolation protocols, testing
regimes (with varying tests), and vaccination requirements.
"""

__author__ = "Cornell Covid Modeling Team"

from . import groups
from . import metrics
from . import micro
from . import plotting
from . import sim
from . import strategy
from . import trajectory
from . import scenario
