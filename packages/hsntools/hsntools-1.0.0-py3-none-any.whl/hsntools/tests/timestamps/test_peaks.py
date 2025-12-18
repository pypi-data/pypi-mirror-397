"""Tests for hsntools.timestamps.peaks"""

import numpy as np

from hsntools.timestamps.peaks import *

###################################################################################################
###################################################################################################

def test_detect_peaks():

    data = np.array([0, 0, 0, 1, 0, 2, 0, 1, 0, 0])
    fs = 10

    height = 0.5
    distance = 1
    thresh = 1.5

    peak_inds, peak_times, peak_heights = detect_peaks(data, fs, height, distance, thresh)

    assert np.array_equal(peak_inds, np.array([3, 7]))
    assert np.allclose(peak_times, np.array([0.3, 0.7]))
    assert np.array_equal(peak_heights, np.array([1., 1.]))
