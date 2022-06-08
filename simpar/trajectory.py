"""Simulation trajectory manager.

Defines a [Trajectory] class which is comprised of a fully run [Sim] that
was the result of applying a given [Strategy] to a [Scenario].
"""

__author__ = "Henry Robbins (henryrobbins)"


from .scenario import Scenario
from .strategy import Strategy
from .sim import Sim


class Trajectory:
    """
    Manages all of the attributes of a simulation run.

    This includes the underlying simulation [Sim] and the scenario [Scenario]
    and the strategy [Strategy] that was used. It also maintains a color and
    name for use when plotting trajectories.
    """

    def __init__(self, scenario: Scenario, strategy: Strategy, sim: Sim,
                 color: str = "black", name: str = None):
        """Initialize a [Trajectory] instance.

        Args:
            scenario (Scenario): Scenario that the simulation was run under.
            strategy (Strategy): Strategy that was used to run the simulation.
            sim (sim): Simulation which used the provided strategy.
            color (str): Color of the trajectory when plotting.
            name (str): Name of the trajectory when plotting.
        """
        self.scenario = scenario
        self.strategy = strategy
        self.sim = sim
        self.color = color
        self.name = strategy.name if name is None else name
