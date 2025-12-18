"""Tests for hsntools.utils.extract"""

import numpy as np

from hsntools.utils.extract import *

###################################################################################################
###################################################################################################

def test_get_event_time():

    times = np.array([0.5, 1.25, 2.5, 3.5])

    out1 = get_event_time(times, 2, 3)
    assert out1 == 2.5

    out2 = get_event_time(times, 4, 5)
    assert np.isnan(out2)

def test_get_trial_value():

    trials = np.array([5, 6, 7, 8, 9])
    data = np.array([10.5, 12.5, 9.5, 7.5, 13.5])

    trial = 5
    out = get_trial_value(trials, data, trial)
    assert isinstance(out, float)
    assert out == 10.5

    trial = 0
    out = get_trial_value(trials, data, trial)
    assert np.isnan(out)
