import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
from typing import List, Callable
from functools import reduce
from operator import iconcat, add
from trajectory import Trajectory
import metrics


def plot_small_summary(outfile : str,
                       trajectories: List[Trajectory]):
    """Plot a small summary of the simulation run."""
    plt.rcParams["figure.figsize"] = (18,16)
    plt.rcParams['font.size'] = 30
    plt.rcParams['lines.linewidth'] = 6
    plt.rcParams['legend.fontsize'] = 22
    plt.subplots_adjust(hspace = 0.8)
    plt.subplot(211)
    plot_total_infected_discovered(trajectories)
    plt.subplot(212)
    plot_isolated(trajectories)
    plt.savefig(outfile, facecolor='w')
    plt.close()

# OBSOLETE, SEE plot_total_infected_discovered
# def plot_infected_discovered(trajectories: List[Trajectory],
#                              popul = None,
#                              metagroup_names : List[str] = None,
#                              legend = True):
#     """Plot infected and discovered for several trajectories.

#     Args:
#         metagroup_names: list of names of meta-group(s) to plot, \
#             None to plot the sum across groups.
#     """
#     # plot each trajectory
#     for trajectory in trajectories:
#         scenario = trajectory.scenario
#         label = trajectory.name
#         s = trajectory.sim
#         color = trajectory.color

#         X = np.arange(s.max_T) * s.generation_time  # days in the semester
#         if metagroup_names == None:
#             discovered = s.get_discovered(aggregate=True, cumulative=True)
#             infected = s.get_infected(aggregate=True, cumulative=True)
#         else:
#             group_idx = popul.metagroup_indices(metagroup_names)
#             group_idx = reduce(iconcat, group_idx, [])  # flatten
#             discovered = s.get_total_discovered_for_different_groups(group_idx, cumulative=True)
#             infected = s.get_total_infected_for_different_groups(group_idx, cumulative=True)
#         if np.isclose(discovered, infected).all():
#             # Discovered and infected are the same, or almost the same.
#             # This occurs when we do surveillance.
#             # Only plot one line.
#             plt.plot(X, discovered, label=label, color=color, linestyle = 'solid')
#         else:
#             plt.plot(X, discovered, label=label + '(Discovered)', color=color, linestyle = 'solid')
#             plt.plot(X, infected, label=label + '(Infected)', color=color, linestyle = 'dashed')

#     if metagroup_names == None:
#         plt.title("Spring Semester Infections, Students+Employees")
#     else:
#         plt.title("Infections " + reduce(add, [scenario["metagroup_names"][x] for x in metagroup_names]))

#     if legend:
#         ax = plt.gca()
#         # Put legend below the current axis because it's too big
#         ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20),
#                   fancybox=True, shadow=True, ncol=2)
#     plt.ylabel('Cumulative Infected')


def plot_isolated(trajectories: List[Trajectory],
                  legend = True,
                  metagroup_names = None):
    """Plot the number of rooms of isolation required to isolate on-campus
    students under the passed set of test regimes.
    popul, metagroups_names and metagroup_idx are only needed if we getting specific metagroups.
    If so,  metagroups_names and metagroup_idx indicate the metagroups that we wish to include
    Turn on the oncampus flag to apply the oncampus_frac
    """
    for trajectory in trajectories:
        label = trajectory.name
        s = trajectory.sim
        color = trajectory.color

        X = np.arange(s.max_T) * s.generation_time  # days in the semester

        isolated = metrics.get_isolated(trajectory=trajectory,
                                        metagroup_names=metagroup_names)

        plt.plot(X, isolated, label=label, color=color)
        if metagroup_names is None:
            plt.title("Isolation (Students+Employees)")
        else:
            plt.title("Isolation (" + str(metagroup_names) + ")")

    if legend:
        plt.legend()
    plt.xlabel('Days')
    plt.ylabel('Isolation (5 day)')


def plot_comprehensive_summary(outfile: str,
                               trajectories: List[Trajectory],
                               simple_param_summary = None):
    """Plot a comprehensive summary of the simulation run."""
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(8.5, 11)
    plt.rcParams.update({'font.size': 8})

    plt.subplot(411) # Take up the whole top row
    plot_total_infected_discovered(trajectories, legend = True)
    window = 423 # Start in the second row

    plt.subplot(window)
    plot_isolated(trajectories, metagroup_names = ['UG_on'],
                  legend = False)
    window += 1

    plt.subplot(window)
    plot_isolated(trajectories, metagroup_names = ['UG_on', 'UG_off',
                                                   'PR_on', 'PR_off'],
                  legend = False)
    window += 1

    # Assumes that every trajectory in [trajectories] has the same population
    popul = trajectories[0].pop
    metagroups = popul.metagroup_names()

    # Plot infected and discovered for each meta-group
    groups = [["UG_on", "UG_off"], ["GR_on", "GR_off"], ["PR_on", "PR_off"], ["FS"]]
    for group in groups:
        plt.subplot(window)
        window += 1
        plot_total_infected_discovered(trajectories, metagroup_names = group, legend = False)

    # def print_params():
    #     if simple_param_summary is None:
    #         plt.text(0,-0.5,param2txt(params))
    #     else:
    #         now = datetime.now()
    #         plt.text(0,0.5,'{}\nSimulation run {}'.format(fill(simple_param_summary, 60),now.strftime('%Y/%m/%d %H:%M')))

    # plt.subplot(window)
    # plt.axis('off')
    # window += 1
    # print_params()

    plt.tight_layout(pad=1)

    plt.savefig(outfile, facecolor='w')
    plt.close()


def plot_parameter_sensitivity(outfile: str, trajectories: List[Trajectory],
    param_name: str, metric_name: str, metric: Callable, title: str = None):
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


def plot_metric_over_time(outfile: str, trajectories: List[Trajectory],
    metric_name: str, metric: Callable, title: str = None, legend = True) -> None:
    """Plot a comparison the [trajectories] for a given [metric] over time.

    The x-axis of the plot is time while the y-axis is the value of the metric.
    Each trajectory is shown as a different line on the plot.

    Args:
        outfile (str): String file path.
        trajectories (List[Trajectory]): List of trajectories to compare.
        metric_name (str): Name of the metric to be plotted.
        metric (Callable): Function to compute the metric.
        title (str, optional): Title of the plot.
        legend (bool, optional): Show legend if True. Defaults to True.
    """
    plt.rcParams["figure.figsize"] = (8,6)
    plt.rcParams['font.size'] = 15
    plt.rcParams['lines.linewidth'] = 6
    plt.rcParams['legend.fontsize'] = 12

    for trajectory in trajectories:
        scenario = trajectory.scenario
        label = trajectory.name
        color = trajectory.color
        x = np.arange(scenario["T"]) * scenario["generation_time"]
        y = metric(trajectory)
        plt.plot(x, y, label=label, color=color, linestyle = 'solid')

    if title is None:
        title = f"{metric_name} over the Spring Semester"
    plt.title(title)
    plt.ylabel(metric_name)
    if legend:
        plt.legend()
    plt.savefig(outfile, facecolor='w')
    plt.close()

def plot_metrics_over_time(trajectories: List[Trajectory],
    metric_names: List[str], metrics: List[Callable], title: str = None, legend = True, metagroup_names = None) -> None:
    """Plot a comparison the [trajectories] for given [metrics] over time (max 4).

    The x-axis of the plot is time while the y-axis is the value of the metric.
    Each trajectory is shown as a different line on the plot.

    Args:
        outfile (str): String file path.
        trajectories (List[Trajectory]): List of trajectories to compare.
        metric_name (str): Name of the metric to be plotted.
        metric (Callable): Function to compute the metric.
        title (str, optional): Title of the plot.
        legend (bool, optional): Show legend if True. Defaults to True.
    """
    assert(len(metric_names)<5)

    linestyles = ['solid', 'dashed', 'dotted', 'dashdot']

    # plt.rcParams["figure.figsize"] = (8,6)
    # plt.rcParams['font.size'] = 10
    # plt.rcParams['lines.linewidth'] = 6
    # plt.rcParams['legend.fontsize'] = 8

    for trajectory in trajectories:
        scenario = trajectory.scenario
        label = trajectory.name
        color = trajectory.color
        x = np.arange(scenario["T"]) * scenario["generation_time"]
        for i in range(len(metrics)):
            y = metrics[i](trajectory, metagroup_names)
            plt.plot(x, y, label=label + ": " + metric_names[i], color=color, linestyle = linestyles[i])

    if title is None:
        if metagroup_names == None:
            plt.title("Spring Semester Infections, Students+Employees")
        else:
            plt.title("Infections " + reduce(add, [scenario["metagroup_names"][x] for x in metagroup_names]))
    else:
        plt.title("Spring Semester")
    plt.ylabel('Cumulative Number')
    if legend:
        ax = plt.gca()
        # Put legend below the current axis because it's too big
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.20),
                  fancybox=True, shadow=True, ncol=2)
    # plt.savefig(outfile, facecolor='w')
    # plt.close()


def plot_hospitalization(outfile, trajectories: List[Trajectory], legend = True):
    """Plot total hospitalizations for multiple trajectories."""
    plot_metric_over_time(outfile=outfile,
                          trajectories=trajectories,
                          metric_name="Cumulative Hospitalizations",
                          metric=metrics.get_cumulative_all_hospitalizations,
                          title="Spring Semester Hospitalizations, Students+Employees",
                          legend=legend)

def plot_total_infected_discovered(trajectories: List[Trajectory], title = None, metagroup_names = None, legend = True):
    """Plot total discovered, including arrival."""
    plot_metrics_over_time(trajectories=trajectories,
                          metric_names=["Discovered", "Infected"],
                          metrics=[metrics.get_total_discovered, metrics.get_total_infected],
                          title=title,
                          metagroup_names = metagroup_names,
                          legend=legend)

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
