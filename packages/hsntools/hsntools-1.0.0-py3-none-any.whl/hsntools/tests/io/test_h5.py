"""Tests for hsntools.io.h5"""

import os

import numpy as np

from hsntools.tests.tsettings import TEST_FILE_PATH

from hsntools.io.h5 import *

###################################################################################################
###################################################################################################

def test_access_h5file():

    f_name = 'test_hdf5'
    h5file = access_h5file(f_name, TEST_FILE_PATH)
    assert h5file
    h5file.close()

def test_open_h5file():

    f_name = 'test_hdf5'
    with open_h5file(f_name, TEST_FILE_PATH) as h5file:
        assert h5file

def test_save_to_h5file():

    tdata = {
        'data1' : np.array([1, 2, 3, 4]),
        'data2' : np.array([1.5, 2.5, 3.5, 4.5]),
    }

    test_fname = 'test_hdf5_saved'

    save_to_h5file(tdata, test_fname, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (test_fname + '.h5'))

def test_load_from_h5file():

    # Note: this test loads data saved from `test_save_to_h5file`
    f_name = 'test_hdf5_saved'

    # Test loading single field
    dataset = load_from_h5file('data1', f_name, TEST_FILE_PATH)
    assert dataset is not None
    assert np.all(dataset['data1'])

    # Test loading multiple fields
    datasets = load_from_h5file(['data1', 'data2'], f_name, TEST_FILE_PATH)
    assert datasets is not None
    assert np.all(datasets['data1'])
    assert np.all(datasets['data2'])
