"""Tests for hsntools.timestamps.utils"""

from hsntools.timestamps.utils import *

###################################################################################################
###################################################################################################

def test_compute_sample_length():

    fs = 1000

    n_samples = 2500
    out2_min = compute_sample_length(n_samples, fs, 'seconds')
    assert out2_min == 2.5

    n_samples = 90000
    out1_min = compute_sample_length(n_samples, fs, 'minutes')
    assert out1_min == 1.5

def test_convert_samples_to_time():

    tfs = 10

    out1 = convert_samples_to_time(10, tfs)
    assert isinstance(out1, np.ndarray)
    assert out1[0] == 0.
    assert len(out1) == tfs

    out2 = convert_samples_to_time(10, tfs, offset=1.)
    assert out2[0] == 1.
    assert len(out2) == tfs

    tsamples = np.array([10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    out3 = convert_samples_to_time(tsamples, tfs)
    assert out3[0] == tsamples[0] / tfs
    assert len(out3) == tfs
