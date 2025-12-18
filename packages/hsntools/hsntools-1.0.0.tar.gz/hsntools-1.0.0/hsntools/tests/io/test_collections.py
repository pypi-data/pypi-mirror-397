"""Tests for hsntools.io.collections"""

import pandas as pd

from hsntools.io.files import save_json

from hsntools.tests.tsettings import TEST_FILE_PATH

from hsntools.io.collections import *

###################################################################################################
###################################################################################################

def test_load_jsons_to_df():

    save_json({'a' : 12, 'b' : 21}, 'test_json_c1', TEST_FILE_PATH)
    save_json({'c' : 13, 'd' : 31}, 'test_json_c2', TEST_FILE_PATH)

    files = ['test_json_c1', 'test_json_c2']
    out = load_jsons_to_df(files, TEST_FILE_PATH)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(files)

    # Test giving a file location
    out = load_jsons_to_df(TEST_FILE_PATH)
    assert isinstance(out, pd.DataFrame)
