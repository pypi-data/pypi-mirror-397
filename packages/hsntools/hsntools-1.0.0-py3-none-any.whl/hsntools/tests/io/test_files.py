"""Tests for hsntools.io.files"""

import os

import numpy as np
import pandas as pd

from hsntools.tests.tsettings import TEST_FILE_PATH

from hsntools.io.files import *

###################################################################################################
###################################################################################################

def test_save_txt():

    text = "Words, words, words."
    f_name = 'test_txt'

    save_txt(text, f_name, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (f_name + '.txt'))

def test_load_txt():

    f_name = 'test_txt'
    text = load_txt(f_name, TEST_FILE_PATH)
    assert text

def test_save_json():

    data = {'a' : 12, 'b' : 21}
    f_name = 'test_json'

    save_json(data, f_name, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (f_name + '.json'))

def test_load_json():

    f_name = 'test_json'
    data = load_json(f_name, TEST_FILE_PATH)
    assert data

def test_save_jsonlines():

    data = [{'A1' : {'a' : 12, 'b' : 21}},
            {'A2' : {'a' : 21, 'b' : 12}}]
    f_name = 'test_jsonlines'

    save_jsonlines(data, f_name, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (f_name + '.json'))

def test_load_jsonlines():

    f_name = 'test_jsonlines'
    data = load_jsonlines(f_name, TEST_FILE_PATH)
    assert data
    assert isinstance(data, dict)
    assert isinstance(data[list(data.keys())[0]], dict)
