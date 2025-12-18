"""Tests for hsntools.io.custom"""

import os

from hsntools.tests.tsettings import TEST_FILE_PATH

from hsntools.io.custom import *

###################################################################################################
###################################################################################################

def test_save_config():

    cdict1 = {'d1' : 1, 'd2' : 'name', 'd3' : ['a', 'b', 'c']}
    f_name1 = 'test_config1'
    save_config(cdict1, f_name1, TEST_FILE_PATH)

    assert os.path.exists(TEST_FILE_PATH / (f_name1 + '.yaml'))

    cdict2 = {'d1' : 'words', 'd2' : None, 'd3' : ['list', 'of', 'terms']}
    f_name2 = 'test_config2'
    save_config(cdict2, f_name2, TEST_FILE_PATH)

    assert os.path.exists(TEST_FILE_PATH / (f_name2 + '.yaml'))

def test_load_config():

    f_name1 = 'test_config1'
    config = load_config(f_name1, TEST_FILE_PATH)
    assert isinstance(config, dict)

def test_load_configs():

    f_names = ['test_config1', 'test_config2']
    configs = load_configs(f_names, TEST_FILE_PATH)
    assert isinstance(configs, dict)

def test_save_object(ttask, tbundle, telectrodes):

    f_name = 'task_obj'
    save_object(ttask, f_name, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (f_name + '.task'))

    f_name = 'bundle_obj'
    save_object(tbundle, f_name, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (f_name + '.bundle'))

    f_name = 'electrodes_obj'
    save_object(telectrodes, f_name, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (f_name + '.electrodes'))

def test_load_object():

    f_name = 'task_obj.task'
    task = load_object(f_name, TEST_FILE_PATH)
    assert task

    f_name = 'bundle_obj.bundle'
    bundle = load_object(f_name, TEST_FILE_PATH)
    assert bundle

    f_name = 'electrodes_obj.electrodes'
    electrodes = load_object(f_name, TEST_FILE_PATH)
    assert electrodes
