"""Settings for tests."""

import os
from pathlib import Path

###################################################################################################
###################################################################################################

# Set base test files path
TESTS_PATH = Path(os.path.abspath(os.path.dirname(__file__)))
BASE_TEST_OUTPUTS_PATH = TESTS_PATH / 'test_outputs'

# Set paths for test files, separated by type
TEST_FILE_PATH = BASE_TEST_OUTPUTS_PATH / 'test_files'
TEST_PLOTS_PATH = BASE_TEST_OUTPUTS_PATH / 'test_plots'
TEST_PROJECT_PATH = BASE_TEST_OUTPUTS_PATH / 'test_project'
TEST_ERRORS_PATH = BASE_TEST_OUTPUTS_PATH / 'test_errors'
TEST_SORTING_PATH = BASE_TEST_OUTPUTS_PATH / 'test_sorting'

# Collect test paths together
TEST_PATHS = {
    'file' : TEST_FILE_PATH,
    'plots' : TEST_PLOTS_PATH,
    'project' : TEST_PROJECT_PATH,
    'errors' : TEST_ERRORS_PATH,
    'sorting' : TEST_SORTING_PATH,
}

# Sorting file settings
TEST_SORT = {
    'channel' : 'test',
    'polarity' : 'neg',
    'user' : 'tes',
}
