"""Tests for hsntools.io.utils"""

from hsntools.io.utils import *

###################################################################################################
###################################################################################################

def test_check_ext():

    f_name = 'test'
    ext = '.txt'

    out1 = check_ext(f_name, ext)
    assert out1 == 'test.txt'

    out2 = check_ext(f_name + '.txt', ext)
    assert out2 == 'test.txt'

def test_drop_ext():

    f_name = 'test'
    ext = '.txt'

    out1 = drop_ext(f_name + ext)
    assert out1 == 'test'

    out2 = drop_ext(f_name)
    assert out2 == 'test'

def test_check_folder():

    folder = 'folder'
    f_name = 'file'

    out1 = check_folder(f_name, folder)
    assert out1 == 'folder/file'

    out2 = check_folder(f_name, None)
    assert out2 == 'file'

def test_drop_hidden_files():

    files = ['.', '.hidden', 'file_a', 'file_b']
    out = drop_hidden_files(files)
    assert out == ['file_a', 'file_b']

def test_drop_file_extensions():

    files = ['file_a.txt', 'file_b.json']
    out = drop_file_extensions(files)
    assert out == ['file_a', 'file_b']

def test_ignore_files():

    files = ['data_1.txt', 'other.txt', 'data_2.txt', 'temp.txt']
    out = ignore_files(files, 'other')
    assert out == ['data_1.txt', 'data_2.txt', 'temp.txt']
    pass

def test_select_files():

    files = ['data_1.txt', 'other.txt', 'data_2.txt', 'temp.txt']
    out = select_files(files, 'data')
    assert out == ['data_1.txt', 'data_2.txt']

def test_sort_files():

    files = ['data_1.txt', 'other.txt', 'data_2.txt', 'temp.txt']
    out = sort_files(files)
    assert out == ['data_1.txt', 'data_2.txt', 'other.txt', 'temp.txt']

def test_make_session_name():

    name1 = make_session_name('subject', 'experiment', 0)
    assert name1 == 'experiment_subject_session_0'

    name2 = make_session_name('subject', 'experiment', 'session_0')
    assert name2 == 'experiment_subject_session_0'

def test_make_file_list():

    files = {'sub1' : ['session1', 'session2'], 'sub2' : ['session1']}
    out = make_file_list('exp', files)
    assert isinstance(out, list)
    assert len(out) == 3
    for el in ['exp_sub1_session1', 'exp_sub1_session2', 'exp_sub2_session1']:
        assert el in out

    out2 = make_file_list('exp', files, ext='.nwb')

def test_file_in_list():

    file_name = 'test.txt'
    file_list1 = ['abc.txt', 'def.txt']
    file_list2 = ['test.txt', 'other_test.txt']

    assert file_in_list(file_name, file_list1) is False
    assert file_in_list(file_name, file_list2) is True

def test_missing_files():

    files = ['session1.nwb', 'session2.nwb', 'session3.nwb']
    compare = ['session1.nwb', 'session2.nwb']

    out = missing_files(files, compare)
    assert out == ['session3.nwb']

def test_get_files():

    out = get_files('.')
    assert isinstance(out, list)

def test_get_subfolders():

    out = get_subfolders('.')
    assert isinstance(out, list)
