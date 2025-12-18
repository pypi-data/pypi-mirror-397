"""Tests for hsntools.paths.paths"""

from hsntools.tests.tsettings import TEST_PROJECT_PATH

from hsntools.paths.paths import *

###################################################################################################
###################################################################################################

def test_paths():

    subject = 'test_subject'
    task = 'test_task'
    session = 'session_0'
    recordings_name = 'test_recordings'

    # Test with minimal info
    paths = Paths(TEST_PROJECT_PATH)
    assert paths

    # Test with all info
    paths = Paths(TEST_PROJECT_PATH, subject, task, session,
                  recordings_name=recordings_name)
    assert paths

    # Test session name
    name = paths.session_name
    assert isinstance(name, str)

    # Test paths defined as properties
    assert paths.recordings
    assert paths.subject
    assert paths.experiment
    assert paths.session

    # Test all the sub-folders that should be defined
    for subdir, subfolders in SESSION_FOLDERS.items():
        assert getattr(paths, subdir)
        for subfolder in subfolders:
            assert getattr(paths, subfolder)
    for subdir in SUBJECT_FOLDERS:
        assert getattr(paths, subdir)
    for subdir in PROJECT_FOLDERS:
       assert getattr(paths, subdir)

    # Check make and get methods with sub-functions
    paths_make_checks(paths)
    paths_get_checks(paths)

def paths_make_checks(paths):

    all_paths = paths._make_all_paths()
    assert all_paths

    session_folders = paths._make_session_folders()
    assert session_folders

    all_folders = paths._make_all_folders()
    assert all_folders

def paths_get_checks(paths):

    for subdir, subfolders in SESSION_FOLDERS.items():
        files = paths.get_files(subdir.split('_')[1])
        assert isinstance(files, list)
        for subfolder in subfolders:
            files = paths.get_files(subdir)
            assert isinstance(files, list)
            subfolders = paths.get_subfolders(subdir)
            assert isinstance(subfolders, list)
    for subdir in SUBJECT_FOLDERS:
        files = paths.get_files(subdir)
        assert isinstance(files, list)
        subfolders = paths.get_subfolders(subdir)
        assert isinstance(subfolders, list)
    for subdir in PROJECT_FOLDERS:
        files = paths.get_files(subdir)
        assert isinstance(files, list)
        subfolders = paths.get_subfolders(subdir)
        assert isinstance(subfolders, list)
