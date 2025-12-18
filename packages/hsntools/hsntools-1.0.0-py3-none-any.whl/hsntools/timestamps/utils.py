"""Utility functions for working with samples and timestamps."""

import numpy as np

###################################################################################################
###################################################################################################

def compute_sample_length(n_samples, fs, output='minutes'):
    """Compute the length of time corresponding to a given number of samples.

    Parameters
    ----------
    n_samples : int
        Number of samples.
    fs : int
        Sampling rate.
    output : {'minutes', 'seconds'}
        The output unit.

    Returns
    -------
    length : float
        Time length for the input number of samples, in unit of `output`.
    """

    assert output in ['minutes', 'seconds'], "Output format not understood."

    n_seconds = n_samples / fs

    if output == 'minutes':
        return n_seconds / 60
    else:
        return n_seconds


def convert_samples_to_time(samples, fs, offset=0):
    """Convert a set of samples to a set of corresponding timestamps.

    Parameters
    ----------
    samples : int or 1d array
        Number of samples to create timestamps for.
    fs : int
        Sampling rate.
    offset : float, optional
        Time value to offset time values by.

    Returns
    -------
    timestamps : 1d array
        Timestamps, in seconds.
    """

    if isinstance(samples, (np.ndarray, list)):
        n_samples = len(samples)
        offset = offset + samples[0] / fs
    else:
        n_samples = samples

    return offset + np.arange(0, n_samples / fs, 1/fs)
