"""Visualizations for checking timestamps."""

from hsntools.modutils.dependencies import safe_import, check_dependency
from hsntools.plts.utils import check_ax, savefig

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_alignment(sync1, sync2, n_pulses=None, ax=None, **plt_kwargs):
    """Plot the alignment between synchronization pulses.

    Parameters
    ----------
    sync1, sync2 : 1d array
        Sync pulse times for each sync pulse stream.
    n_pulses : int, optional
        Restrict the visualization to a restricted number of pulses.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', (20, 4)))

    ax.eventplot([sync1, sync2], linelengths=[0.9, 0.9], colors=['g', 'b'])
    ax.set_xlabel('Time')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Sync Neural', 'Sync Behavioral'])
    ax.set_title('Synchronization pulses')

    if n_pulses:
        ax.set_xlim(sync1[0], sync1[n_pulses])


@savefig
@check_dependency(plt, 'matplotlib')
def plot_peaks(data, peak_inds, peak_heights, ax=None, **plt_kwargs):
    """Plot detected peaks on a time series.

    Parameters
    ----------
    data : 1d array
        Time series data.
    peak_inds : 1d array
        Indices of the detected peaks.
    peak_heights : 1d array
        Heights of the detected peaks.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    ax = check_ax(ax, figsize=plt_kwargs.pop('figsize', (12, 4)))

    ax.plot(data)
    ax.plot(peak_inds, peak_heights, '.')
