"""Tests for hsntools.io.nwb"""

import os

from hsntools.tests.tsettings import TEST_FILE_PATH

from hsntools.io.nwb import *

###################################################################################################
###################################################################################################

def test_save_nwbfile(tnwbfile):

    test_fname = 'test_nwbfile'
    save_nwbfile(tnwbfile, test_fname, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (test_fname + '.nwb'))

def test_load_nwbfile():

    test_fname = 'test_nwbfile'
    tnwbfile = load_nwbfile(test_fname, TEST_FILE_PATH)
    assert tnwbfile
