"""Pytest configuration file for testing hsntools."""

import os
import shutil
from datetime import datetime
from dateutil.tz import tzlocal

import numpy as np

from pynwb import NWBFile

import pytest

from hsntools.io.h5 import open_h5file
from hsntools.objects.task import TaskBase
from hsntools.objects.electrodes import Bundle, Electrodes
from hsntools.tests.tsettings import BASE_TEST_OUTPUTS_PATH, TEST_PATHS, TEST_SORT

###################################################################################################
###################################################################################################

## TEST SETUP

@pytest.fixture(scope='session', autouse=True)
def check_dir():
    """Once, prior to session, this will clear and re-initialize the test file directories."""

    # If the directories already exist, clear them
    if os.path.exists(BASE_TEST_OUTPUTS_PATH):
        shutil.rmtree(BASE_TEST_OUTPUTS_PATH)

    # Remake base test outputs path, and then each sub-directory
    os.mkdir(BASE_TEST_OUTPUTS_PATH)
    for name, TEST_PATH in TEST_PATHS.items():
        os.mkdir(TEST_PATH)

    # Make combinato format file structure for testing sorting files
    chan_dir = 'chan_{}'.format(TEST_SORT['channel'])
    sort_dir = 'sort_{}_{}'.format(TEST_SORT['polarity'], TEST_SORT['user'])
    os.mkdir(TEST_PATHS['sorting'] / chan_dir)
    os.mkdir(TEST_PATHS['sorting'] / chan_dir / sort_dir)
    os.mkdir(TEST_PATHS['sorting'] / 'units')

## TEST OBJECTS

@pytest.fixture(scope='session')
def tnwbfile():
    """Create a test NWBfile."""

    yield NWBFile('session_desc', 'session_id', datetime.now(tzlocal()))

@pytest.fixture(scope='session')
def tunits():
    """Create a test units dictionary."""

    n_units = 5

    yield {
        'ind' : 0,
        'channel' : 'chan_0',
        'polarity' : 'neg',
        'times' : np.arange(n_units),
        'waveforms' : np.ones([n_units, 64]),
        'classes' : np.array([0, 1, 0, 1, 0]),
        'clusters' : np.array([1, 2, 3, 1, 2]),
    }

@pytest.fixture(scope='session')
def tbundle():
    """Create a test bundle object."""

    yield Bundle('tname1', 'themi1', 'tlobe1', 'tregion1')

@pytest.fixture(scope='session')
def telectrodes():
    """Create a test electrodes object."""

    electrodes = Electrodes('subject', 30000)
    electrodes.add_bundles([
        {'probe' : 'tname1', 'hemisphere' : 'themi1', 'lobe' : 'tlobe1', 'region' : 'tregion1'},
        {'probe' : 'tname2', 'hemisphere' : 'themi2', 'lobe' : 'tlobe2', 'region' : 'tregion2'},
    ])

    yield electrodes

@pytest.fixture(scope='session')
def ttask():
    """Create a test task object."""

    yield TaskBase()

@pytest.fixture(scope='session')
def ttask_full():
    """Create a test task object."""

    task = TaskBase()
    task.trial['trial'] = [0, 1, 2]
    task.trial['start_time'] = [0, 1, 2]
    task.trial['stop_time'] = [1, 2, 3]
    task.trial['type'] = ['a', 'b', 'c']
    task.trial['field1'] = ['a', 'b', 'c']
    task.trial['field2'] = [1, 2, 3]

    yield task

@pytest.fixture(scope='session', autouse=True)
def th5file():
    """Save out a test HDF5 file."""

    with open_h5file('test_hdf5.h5', TEST_PATHS['file'], mode='w') as h5file:
        dset1 = h5file.create_dataset("data", data=np.ones(10), dtype='i')
        dset2 = h5file.create_dataset("data2", data=np.ones(10), dtype='f')

@pytest.fixture(scope='session', autouse=True)
def spike_data_file():
    """Save out a test combinato spike data file."""

    chan_dir = 'chan_{}'.format(TEST_SORT['channel'])
    full_path = TEST_PATHS['sorting'] / chan_dir

    n_spikes = 5
    with open_h5file('data_chan_test.h5', full_path, mode='w') as h5file:
        dgroup = h5file.create_group('neg')
        dgroup.create_dataset('times', data=np.ones(n_spikes), dtype='f')
        dgroup.create_dataset('spikes', data=np.ones([n_spikes, 64]), dtype='f')
        dgroup.create_dataset('artifacts', data=np.ones(n_spikes), dtype='i')

@pytest.fixture(scope='session', autouse=True)
def sort_data_file():
    """Save out a test combinato spike sorting file."""

    chan_dir = 'chan_{}'.format(TEST_SORT['channel'])
    sort_dir = 'sort_{}_{}'.format(TEST_SORT['polarity'], TEST_SORT['user'])
    full_path = TEST_PATHS['sorting'] / chan_dir / sort_dir

    n_spikes = 5
    with open_h5file('sort_cat.h5', full_path, mode='w') as h5file:
        h5file.create_dataset('groups', data=np.array([[0, 0], [1, -1], [2, 1]]), dtype='i')
        h5file.create_dataset('index', data=np.array([0, 1, 2, 3, 4]), dtype='i')
        h5file.create_dataset('classes', data=np.array([0, 1, 2, 0, 1]), dtype='i')
