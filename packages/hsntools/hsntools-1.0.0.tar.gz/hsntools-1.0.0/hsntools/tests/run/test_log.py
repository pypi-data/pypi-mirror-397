"""Tests for hsntools.run.log"""

from hsntools.run.log import *

###################################################################################################
###################################################################################################

def test_print_status():

    print_status(True, 'words, words, words', 1)
    print_status(False, 'words, words, words', 2)
