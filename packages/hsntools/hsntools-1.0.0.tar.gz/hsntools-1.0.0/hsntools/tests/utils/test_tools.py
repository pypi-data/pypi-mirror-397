"""Tests for hsntools.utils.tools"""

import inspect

from hsntools.utils.tools import *

###################################################################################################
###################################################################################################

def test_incrementer():

    # Test basic usage
    start, end = 0, 5
    inc = incrementer(start, end)
    assert inspect.isgenerator(inc)
    out = next(inc)
    assert isinstance(out, int)

    # Check giving specified range
    start, end = 5, 10
    inc = incrementer(start, end)
    for value in inc:
        assert isinstance(value, int)
        assert value < end
