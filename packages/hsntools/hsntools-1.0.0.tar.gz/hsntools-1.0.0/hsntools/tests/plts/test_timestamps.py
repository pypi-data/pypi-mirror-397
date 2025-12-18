"""Tests for hsntools.plts.timestamps"""

import numpy as np

from hsntools.tests.tutils import plot_test
from hsntools.tests.tsettings import TEST_PLOTS_PATH

from hsntools.plts.timestamps import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_alignment():

    arr1 = [1, 2, 3, 4, 5]
    arr2 = [1, 2, 3, 4, 5]

    plot_alignment(arr1, arr2,
                   file_path=TEST_PLOTS_PATH, file_name='tplot_alignment.png')

@plot_test
def test_plot_peaks():

    data = np.array([0, 0, 0, 1, 0, 0, 0, 1, 0, 0])

    peak_inds = np.array([3, 7])
    peak_heights = np.array([1, 1])

    plot_peaks(data, peak_inds, peak_heights,
               file_path=TEST_PLOTS_PATH, file_name='tplot_peaks.png')
