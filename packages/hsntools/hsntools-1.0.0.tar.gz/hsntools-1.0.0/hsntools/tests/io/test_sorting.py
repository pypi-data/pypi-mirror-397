"""Tests for hsntools.io.sorting"""

import os
from copy import deepcopy

from hsntools.tests.tsettings import TEST_FILE_PATH, TEST_SORTING_PATH, TEST_SORT

from hsntools.io.sorting import *

###################################################################################################
###################################################################################################

def test_load_combinato_spike_file():

    sdata = load_combinato_spike_file('test', TEST_SORTING_PATH, 'neg')
    for label in ['channel', 'polarity', 'times', 'waveforms', 'artifacts']:
        assert label in sdata

def test_load_combinato_sorting_file():

    sdata = load_combinato_sorting_file(TEST_SORT['channel'], TEST_SORTING_PATH,
                                        TEST_SORT['polarity'], TEST_SORT['user'])
    for label in ['channel', 'polarity', 'groups', 'index', 'classes']:
        assert label in sdata

def test_save_units(tunits):

    tunits2 = deepcopy(tunits)
    tunits2['ind'] = 1

    units = [tunits, tunits2]
    save_units(units, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / 'times_chan_0_u0.h5')
    assert os.path.exists(TEST_FILE_PATH / 'times_chan_0_u1.h5')

def test_load_units():

    units = load_units(TEST_FILE_PATH)
    assert isinstance(units, list)
    assert isinstance(units[0], dict)
    assert len(units) == 2
    for unit in units:
        for field in ['ind', 'channel', 'polarity', 'times', 'waveforms', 'classes']:
            assert field in unit
