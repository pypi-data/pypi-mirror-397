"""Tests for hsntools.utils.convert"""

import numpy as np

from hsntools.utils.convert import *

###################################################################################################
###################################################################################################

def test_convert_str_to_bool():

    assert convert_str_to_bool('True')
    assert not convert_str_to_bool('False')

def test_convert_strlist_to_bool():

    lst = ['False', 'True', 'False']
    assert convert_strlist_to_bool(lst) == [False, True, False]

def test_convert_type():

    var = '12'
    out = convert_type(var, int)
    assert out == 12
    assert isinstance(out, int)

def test_convert_to_array():

    data = ['1', '2', '3']

    out1 = convert_to_array(data, int)
    assert isinstance(out1, np.ndarray)
    assert len(data) == len(out1)
    assert 'int' in str(out1.dtype)

    out2 = convert_to_array(data, float)
    assert 'float' in str(out2.dtype)
