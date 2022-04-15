import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
from typing import List, Callable
from copy import deepcopy
from .trajectory import Trajectory
from . import metrics


# ===========================
# Plot lines on existing Axes
# ===========================

def _add_metric_confidence_interval(ax,
                                    trajectories: List[Trajectory],
                                    metric: Callable,
                                    confidence_interval=0.95,
                                    comparator: Callable = np.sum,
                                    zorder=0):
    """Add confidence interval of [metric] to the axes [ax]."""
    # sort the trajectories
    scenario = trajectories[0].scenario
    x = np.arange(scenario["T"]) * scenario["generation_time"]
    ys = [metric(trajectory) for trajectory in trajectories]
    ys = sorted(ys, key=comparator)

    # compute the confidence interval
    limit = ((1 - confidence_interval) / 2)
    lb = ys[int(len(ys) * limit)]
    nominal = ys[int(len(ys) * 0.5)]
    ub = ys[int(len(ys) * (1 - limit))]

    # add confidence interval to plot
    name = trajectories[0].strategy.name
    color = trajectories[0].color
    ax.plot(x, nominal, label=f"Nominal (50%) [{name}]", color=color,
            linestyle="solid", zorder=zorder)
    # TODO (hwr26): Maybe have an argument that flags this on/off?
    # ax.plot(x, lb, label=f"Optimistic (5%) [{name}]", color=color,
    #         linestyle="dashed", zorder=zorder)
    ax.plot(x, ub, label=f"Pessimistic (95%) [{name}]", color=color,
            linestyle="dashed", zorder=zorder)

    # ax.fill_between(x, ub, lb, label=ci_label, alpha=0.25,
    #                 color=color, zorder=zorder)


def _add_trajectory_metric(ax,
                           trajectory: Trajectory,
                           metric: Callable,
                           linestyle: str = "solid") -> None:
    """Add the [metric] for the [trajectory] to the axes [ax]."""
    scenario = trajectory.scenario
    label = trajectory.name
    color = trajectory.color
    x = np.arange(scenario["T"]) * scenario["generation_time"]
    y = metric(trajectory)
    ax.plot(x, y, label=label, color=color, linestyle=linestyle)


# =======================
# Initialize helpful Axes
# =======================


def _metric_over_time_axes(ax,
                           trajectories: List[Trajectory],
                           metric_name: str,
                           metric: Callable,
                           title: str = None,
                           legend=True):
    """Set [ax] to plot [trajectories] for a given [metric] over time."""
    for trajectory in trajectories:
        _add_trajectory_metric(ax, trajectory, metric)
    if title is None:
        title = f"{metric_name} over the Spring Semester"
    ax.set_title(title)
    ax.set_ylabel(metric_name)
    ax.set_xlabel("Time (Days)")
    if legend:
        ax.legend()


def _metrics_over_time_axes(ax,
                            trajectories: List[Trajectory],
                            metric_names: List[str],
                            metrics: List[Callable],
                            title: str = None,
                            ylabel: str = None,
                            legend=True) -> None:
    """Set [ax] to plot [trajectories] for a given [metrics] over time."""
    linestyles = ['solid', 'dashed', 'dotted', 'dashdot']
    for i in range(len(metrics)):
        for trajectory in trajectories:
            trajectory = deepcopy(trajectory)
            trajectory.name = f"{trajectory.name} ({metric_names[i]})"
            _add_trajectory_metric(ax, trajectory, metrics[i], linestyles[i])
    # TODO (hwr): Make this correct
    if ylabel is None:
        ylabel = metric_names[0]
    if title is None:
        title = f"{ylabel} over the Spring Semester"
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Time (Days)")
    if legend:
        ax.legend()


def _metric_confidence_interval_over_time_axes(ax,
                                               trajectories: List[Trajectory],
                                               metric_name: str,
                                               metric: Callable,
                                               title: str = None,
                                               legend=True,
                                               comparator: Callable = np.sum
                                               ) -> None:
    """Set [ax] to plot 95% confidence interval of [metric] over time."""
    _add_metric_confidence_interval(ax=ax,
                                    trajectories=trajectories,
                                    metric=metric,
                                    confidence_interval=0.95,
                                    comparator=comparator)
    if title is None:
        title = f"{metric_name} over Spring Semester"
    ax.set_title(title)
    ax.set_ylabel(metric_name)
    ax.set_xlabel("Time (Days)")
    if legend:
        ax.legend()


def _metric_confidence_intervals_over_time_axes(ax,
                                                trajectories: List[List[Trajectory]],
                                                metric_name: str,
                                                metric: Callable,
                                                title: str = None,
                                                legend=True,
                                                comparator: Callable = np.sum
                                                ) -> None:
    """Set [ax] to plot [trajectories] CI for a given [metric] over time."""
    for i in range(len(trajectories)):
        trajs = deepcopy(trajectories[i])
        _add_metric_confidence_interval(ax, trajs, metric,
                                        comparator=comparator, zorder=i)
    if title is None:
        title = f"{metric_name} over the Spring Semester"
    ax.set_title(title)
    ax.set_ylabel(metric_name)
    ax.set_xlabel("Time (Days)")
    if legend:
        # TODO (hwr26): Provide as argument?
        ax.legend(loc="upper left")


# =================
# Single Axes Plots
# =================

def plot_metric_over_time(outfile: str,
                          trajectories: List[Trajectory],
                          metric_name: str,
                          metric: Callable,
                          title: str = None):
    """Plot the [trajectories] for a given [metric] over time.

    The x-axis of the plot is time while the y-axis is the value of the metric.

    Args:
        outfile (str): String file path.
        trajectories (List[Trajectory]): List of trajectories to compare.
        metric_name (str): Name of the metric to be plotted.
        metric (Callable): Function to compute the metric.
        title (str, optional): Title of the plot.
    """
    fig, ax = plt.subplots()
    _metric_over_time_axes(
        ax=ax,
        trajectories=trajectories,
        metric_name=metric_name,
        metric=metric,
        title=title,
        legend=True
    )
    fig.savefig(outfile, facecolor='w')


def plot_metrics_over_time(outfile: str,
                           trajectories: List[Trajectory],
                           metric_names: List[str],
                           metrics: List[Callable],
                           title: str = None,
                           ylabel: str = None):
    """Plot the [trajectories] for the given [metrics] over time.

    The x-axis of the plot is time while the y-axis is the value of the metric.

    Args:
        outfile (str): String file path.
        trajectories (List[Trajectory]): List of trajectories to compare.
        metric_names (List[str]): Name of the metrics to be plotted.
        metrics (List[Callable]): Function to compute the metrics.
        title (str, optional): Title of the plot.
        ylabel (str, optional): y-label of the plot.
    """
    fig, ax = plt.subplots()
    _metrics_over_time_axes(
        ax=ax,
        trajectories=trajectories,
        metric_name=metric_names[0],
        metric=metrics[0],
        title=title,
        ylabel=ylabel,
        legend=True
    )
    fig.savefig(outfile, facecolor='w')


def plot_metric_confidence_interval_over_time(outfile: str,
                                              trajectories: List[Trajectory],
                                              metric_name: str,
                                              metric: Callable,
                                              title: str = None,
                                              legend=True,
                                              comparator: Callable = np.sum
                                              ) -> None:
    """Plot the 95% confidence interval of [metric] over time.

    The x-axis of the plot is time while the y-axis is the value of the metric.

    Args:
        outfile (str): String file path.
        trajectories (List[Trajectory]): List of trajectories to compute \
            the confidence interval from.
        metric_name (str): Name of the metric to be plotted.
        metric (Callable): Function to compute the metric.
        title (str, optional): Title of the plot.
        legend (bool, optional): Show legend if True. Defaults to True.
        comparator (Callable): How trajectories are sorted. Defaults to area \
            under the curve (np.sum).
    """
    fig, ax = plt.subplots()
    _metric_confidence_interval_over_time_axes(
        ax=ax,
        trajectories=trajectories,
        metric_name=metric_name,
        metric=metric,
        title=title,
        legend=legend,
        comparator=comparator
    )
    fig.savefig(outfile, facecolor='w')


def plot_isolated(outfile: str,
                  trajectories: List[Trajectory],
                  metagroup_names=None) -> None:
    """Plot the isolated count by day for each trajectory."""
    metric = lambda x: metrics.get_isolated(x, metagroup_names=metagroup_names)
    plot_metric_over_time(outfile=outfile,
                          trajectories=trajectories,
                          metric_name=f"Isolations ({metagroup_names})",
                          metric=metric,
                          title=f"Isolations ({metagroup_names}) over Spring Semester")


def plot_hospitalization(outfile: str, trajectories: List[Trajectory]):
    """Plot total hospitalizations for multiple trajectories."""
    plot_metric_over_time(outfile=outfile,
                          trajectories=trajectories,
                          metric_name="Cumulative Hospitalizations",
                          metric=metrics.get_cumulative_all_hospitalizations,
                          title="Spring Semester Hospitalizations, Students+Employees")


def plot_total_infected_discovered(trajectories: List[Trajectory],
                                   metagroup_names=None) -> None:
    """Plot total discovered, including arrival."""
    plot_metric_over_time(trajectories=trajectories,
                          metric_names=["Infected", "Discvoered"],
                          metrics=[metrics.get_total_infected, metrics.get_total_discovered],
                          title=f"Infections ({metagroup_names}) over Spring Semester",
                          metagroup_names=metagroup_names)


def plot_parameter_sensitivity(outfile: str,
                               trajectories: List[Trajectory],
                               param_name: str,
                               metric_name: str,
                               metric: Callable,
                               title: str = None):
    """Plot a comparison of some [metric] over different values of a parameter.

    The x-axis of the plot is the value of the parameter (stored in the name
    of the trajectory) while the y-axis is the value of the metric.

    Args:
        outfile (str): String file path.
        trajectories (List[Trajectory]): List of trajectories to compare.
        param_name (str): Name of the parameter to be adjusted.
        metric_name (str): Name of the metric to be plotted.
        metric (Callable): Function to compute the metric.
        title (str, optional): Title of the plot.
        legend (bool, optional): Show legend if True. Defaults to True.
    """
    plt.rcParams["figure.figsize"] = (8,6)
    plt.rcParams['font.size'] = 15
    plt.rcParams['lines.linewidth'] = 6
    plt.rcParams['legend.fontsize'] = 12

    x = [float(traj.name) for traj in trajectories]
    y = [metric(traj) for traj in trajectories]
    plt.plot(x, y, linestyle = 'solid')

    if title is None:
        title = f"{param_name} vs. {metric_name}"
    plt.title(title)
    plt.xlabel(param_name)
    plt.ylabel(metric_name)
    plt.savefig(outfile, facecolor='w')
    plt.close()


# ===================
# Multiple Axes Plots
# ===================

def plot_small_summary(outfile: str,
                       trajectories: List[Trajectory]):
    """Plot a small summary of the simulation run."""
    plt.rcParams["figure.figsize"] = (18,16)
    plt.rcParams['font.size'] = 30
    plt.rcParams['lines.linewidth'] = 6
    plt.rcParams['legend.fontsize'] = 22
    plt.subplots_adjust(hspace=0.8)
    plt.subplot(211)
    plot_total_infected_discovered(trajectories)
    plt.subplot(212)
    plot_isolated(trajectories)
    plt.savefig(outfile, facecolor='w')
    plt.close()


def plot_comprehensive_summary(outfile: str, trajectories: List[Trajectory]):
    """Plot a comprehensive summary of the simulation run."""
    fig, axs = plt.subplots(4,2)
    axs = list(axs.flat)
    fig.tight_layout(pad=1)
    fig.subplots_adjust(left=0.1)
    fig.set_size_inches(8.5, 11)

    _metrics_over_time_axes(
        ax=plt.subplot(411),
        trajectories=trajectories,
        metric_names=["Infected", "Discvoered"],
        metrics=[metrics.get_total_infected, metrics.get_total_discovered],
        title=f"Infections over Spring Semester",
        ylabel="Infections"
    )

    _metric_over_time_axes(
        ax=axs[2],
        trajectories=trajectories,
        metric_name="On-Campus UGs Isolated",
        metric=metrics.get_ug_on_isolated,
        legend=False
    )

    _metric_over_time_axes(
        ax=axs[3],
        trajectories=trajectories,
        metric_name="Hospitalizations",
        metric=metrics.get_cumulative_all_hospitalizations,
        legend=False
    )

    group_names = ["UG", "GR", "PR", "FS"]
    groups = [["UG_on", "UG_off"], ["GR_on", "GR_off"], ["PR_on", "PR_off"], ["FS"]]
    for i in range(4):
        metric = lambda x: metrics.get_total_discovered(x, metagroup_names=groups[i])
        _metric_over_time_axes(
            ax=axs[4+i],
            trajectories=trajectories,
            metric_name=f"{group_names[i]} Discovered",
            metric=metric,
            legend=False
        )

    fig.savefig(outfile, facecolor='w')


def plot_comprehensive_confidence_interval_summary(outfile: str,
    trajectories: List[List[Trajectory]]) -> None:
    """Plot comprehensive summary of multiple trajectories sampled from prior."""
    fig, axs = plt.subplots(2,2)
    axs = list(axs.flat)
    fig.tight_layout(pad=1)
    fig.subplots_adjust(left=0.1)
    fig.set_size_inches(11, 8.5)

    _metric_confidence_intervals_over_time_axes(
        ax=axs[0],
        trajectories=trajectories,
        metric_name="Total Infected",
        metric=metrics.get_total_infected,
        comparator=lambda x: x[-1],
        legend=True
    )

    _metric_confidence_intervals_over_time_axes(
        ax=axs[1],
        trajectories=trajectories,
        metric_name="Total Detected",
        metric=metrics.get_total_discovered,
        comparator=lambda x: x[-1],
        legend=False
    )

    _metric_confidence_intervals_over_time_axes(
        ax=axs[2],
        trajectories=trajectories,
        metric_name="On-Campus UGs Isolated",
        metric=metrics.get_ug_on_isolated,
        legend=False
    )

    _metric_confidence_intervals_over_time_axes(
        ax=axs[3],
        trajectories=trajectories,
        metric_name="Hospitalizations",
        metric=metrics.get_cumulative_all_hospitalizations,
        legend=False,
        comparator=lambda x: x[-1]
    )

    fig.savefig(f"{outfile}_summary.png", facecolor='w')

    # clear axes
    for i in range(4):
        axs[i].clear()

    group_names = ["UG", "GR", "PR", "FS"]
    groups = [["UG_on", "UG_off"], ["GR_on", "GR_off"], ["PR_on", "PR_off"], ["FS"]]
    for i in range(4):
        metric = lambda x: metrics.get_total_discovered(x, metagroup_names=groups[i])
        _metric_confidence_intervals_over_time_axes(
            ax=axs[i],
            trajectories=trajectories,
            metric_name=f"{group_names[i]} Detected",
            metric=metric,
            comparator=lambda x: x[-1],
            legend=False
        )
    axs[0].legend(loc="upper left")

    fig.savefig(f"{outfile}_discovered.png", facecolor='w')

# ======================
# CSV Summary Statistics
# ======================

def param2txt(params):
    param_txt = ''
    for param_name in params:
        param = params[param_name]
        if param_name == 'meta_matrix':
            np.set_printoptions(precision = 2)
            param_txt = param_txt + '\nmeta_matrix:\n' + str(np.matrix(param))
        elif param_name == 'pop_fracs':
            # skip
            1 == 1
        elif param_name == 'population_names':
            param_txt +=  f"\n{param_name}: {str(list(param.keys()))}"
        else:
            param_txt = param_txt + '\n' + param_name + ':' + str(param)
    return param_txt


def summary_statistics(outfile: str,
                       trajectories: List[Trajectory]):
    """Output a CSV file with summary statistics"""
    df = {}
    df["Hotel Room Peaks"] = \
        {t.strategy.name : metrics.get_peak_hotel_rooms(t) for t in trajectories}
    df["Total Hotel Rooms"] = \
        {t.strategy.name : metrics.get_total_hotel_rooms(t) for t in trajectories}
    df["UG+PR Days In Isolation In Person"] = \
        {t.strategy.name: metrics.get_ug_prof_days_in_isolation_in_person(t) for t in trajectories}
    df["UG+PR Days In Isolation (All Time)"] = \
        {t.strategy.name: metrics.get_ug_prof_days_in_isolation(t) for t in trajectories}
    df["Hospitalizations"] = \
        {t.strategy.name : metrics.get_total_hospitalizations(t) for t in trajectories}
    df["Cumulative Infections"] = \
        {t.strategy.name : metrics.get_cumulative_infections(t) for t in trajectories}
    pd.DataFrame(df).T.to_csv(outfile)
