"""Utility functions for extracting values."""

import numpy as np

from hsntools.utils.convert import convert_type

###################################################################################################
###################################################################################################

def get_event_time(event_times, start, end):
    """Select a (single) event based on time range, returning NaN if not found.

    Parameters
    ----------
    event_times : 1d array
        Event times.
    start, end : float
        Start and end times to select between.

    Returns
    -------
    event : float or np.nan
        The selected event time, if found, or NaN.
    """

    try:
        event = event_times[np.logical_and(event_times >= start, event_times <= end)][0]
    except IndexError:
        event = np.nan

    return event


def get_trial_value(trials, data, trial, dtype=None):
    """Extract a value for a specified trial.

    Parameters
    ----------
    trials : 1d array
        The set of trial number for which the data is defined.
    data : 1d array
        Data corresponding to each trial number in `trials`.
    trial : int
        The trial number to extract.
    dtype : type, optional
        If provided, provides a type to cast output value to.

    Returns
    -------
    out
        The extracted data value for the given trial number.
        If `trial` is not availabe, returns np.nan.
    """

    if trial in trials:
        out = data[trials == trial][0]
    else:
        out = np.nan

    if dtype:
        out = convert_type(out, dtype)

    return out
