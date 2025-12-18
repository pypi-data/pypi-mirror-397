"""Tests for hsntools.timestamps.dates"""

from datetime import datetime

from hsntools.timestamps.dates import *

###################################################################################################
###################################################################################################

def test_get_current_date():

    date = get_current_date()
    assert isinstance(date, datetime)

def test_convert_time_to_date():

    date = convert_time_to_date(1234567891)
    assert isinstance(date, datetime)
