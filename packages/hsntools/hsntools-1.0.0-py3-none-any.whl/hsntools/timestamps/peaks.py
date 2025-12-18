"""Functions for working with peaks."""

import numpy as np

from hsntools.timestamps.utils import convert_samples_to_time
from hsntools.modutils.dependencies import safe_import, check_dependency

signal = safe_import('.signal', 'scipy')

###################################################################################################
###################################################################################################

@check_dependency(signal, 'scipy')
def detect_peaks(data, fs, height, distance=None, thresh=None):
    """Process peaks from a time series.

    Parameters
    ----------
    data : 1d array
        Data to detect peaks from.
    fs : int
        Sampling rate of the time series.
    height : float
        Required minimum height of peaks.
    distance : float, optional
        Required minimal number of samples between neighbouring peaks.
    thresh : float, optional
        A maximum height of peaks. If provided, peaks above this threshold are dropped.

    Returns
    -------
    peak_inds : 1d array
        Indices of the detected peaks.
    peak_times : 1d array
        Timestamps of the detected peaks, in seconds.
    peak_heights : 1d array
        Heights of the detected peaks, in units of the original data.
    """

    # Detect peaks in the time series
    peak_inds, properties = signal.find_peaks(data, height=height, distance=distance)
    peak_heights = properties['peak_heights']

    # Drop peaks that go beyond a threshold value (if provided)
    if thresh:
        mask = peak_heights < thresh
        peak_inds = peak_inds[mask]
        peak_heights = peak_heights[mask]

    # Convert peak indices to time stamps (in seconds)
    timestamps = convert_samples_to_time(len(data), fs)
    peak_times = np.array([timestamps[peak] for peak in peak_inds])

    return peak_inds, peak_times, peak_heights
