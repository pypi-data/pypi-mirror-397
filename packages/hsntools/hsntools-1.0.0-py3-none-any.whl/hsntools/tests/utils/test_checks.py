"""Tests for hsntools.utils.checks"""

from hsntools.utils.checks import *

###################################################################################################
###################################################################################################

def test_is_empty():

    assert is_empty(None)
    assert is_empty('')
    assert is_empty(0)
    assert is_empty([])
    assert is_empty(np.array([]))
    assert not is_empty('abc')
    assert not is_empty(12)
    assert not is_empty([1, 2])
    assert not is_empty(np.array([1, 2]))

def test_is_type():

    assert is_type(10, None)
    assert is_type(10, int)
    assert not is_type(10, str)

def test_check_str_contents():

    str_to_check = 'TEST_WORDS_IN_STRING'

    # Test single string input
    content_in = 'TEST'
    content_not_in = 'OTHER'
    assert check_str_contents(str_to_check, content_in)
    assert not check_str_contents(str_to_check, content_not_in)

    # Test list of string inputs
    contents_in = ['TEST', 'OTHER']
    assert check_str_contents(str_to_check, contents_in)
    contents_not_in = ['OTHER', 'ALSO']
    assert not check_str_contents(str_to_check, contents_not_in)

def test_clean_strings():

    strs = ['word', 12, 'More words', None]

    out = clean_strings(strs)
    assert isinstance(out, list)
    for el in out:
        assert isinstance(el, str)
