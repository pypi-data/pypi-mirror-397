"""Tests for hsntools.objects.task"""

import numpy as np
import pandas as pd

from pytest import raises

from hsntools.utils.convert import convert_to_array

from hsntools.objects.task import *

###################################################################################################
###################################################################################################

def test_task_base():

    task = TaskBase()
    assert task

def test_task_check_field():

    task = TaskBase()
    task._check_field('trial')

    with raises(AssertionError):
        task._check_field('not_a_thing')

def test_task_add_metadata():

    task = TaskBase()
    task.add_metadata('subject', 'experiment', 'session')
    assert task.meta['subject'] == 'subject'
    assert task.meta['experiment'] == 'experiment'
    assert task.meta['session'] == 'session'

def test_task_set_status():

    task = TaskBase()
    task.set_status('time_aligned', True)

def test_task_set_info():

    task = TaskBase()
    task.set_info('time_offset', 10)

def test_task_data_keys():

    task = TaskBase()
    keys = task.data_keys()
    assert 'status' not in keys
    for attribute in ['trial', 'responses', 'sync', 'session']:
        assert attribute in keys

    # Test adding custom attribute
    task.custom = None
    assert 'custom' in task.data_keys()

def test_task_drop_fields():

    task = TaskBase()

    drop_field = 'session'
    assert getattr(task, drop_field)
    task.drop_fields(drop_field)
    with raises(AttributeError):
        getattr(task, drop_field)

    drop_fields = ['position', 'head_direction']
    for field in drop_fields:
        assert getattr(task, field)

    task.drop_fields(drop_fields)
    for field in drop_fields:
        with raises(AttributeError):
            getattr(task, field)

def test_task_drop_keys():

    task = TaskBase()

    field = 'experiment'
    drop_key = 'language'
    assert drop_key in getattr(task, field)
    task.drop_keys(field, drop_key)
    assert drop_key not in getattr(task, field)

    field ='position'
    drop_keys = ['y', 'z']
    for key in drop_keys:
        assert key in getattr(task, field)
    task.drop_keys(field, drop_keys)
    for key in drop_keys:
        assert key not in getattr(task, field)

def test_task_apply_func_to_fields():

    def plus_func(data, plus):
        return [el + plus for el in data]

    task = TaskBase()
    task.trial['stuff'] = [1, 2, 3]
    task.apply_func('trial', 'stuff', plus_func, plus=1)
    assert task.trial['stuff'] == [2, 3, 4]

    task = TaskBase()
    task.trial['outer'] = {}
    task.trial['outer']['inner1'] = [1.5, 2.5, 3.5]
    task.trial['outer']['inner2'] = [2.5, 3.5, 4.5]
    task.apply_func('trial', {'outer' : ['inner1', 'inner2']}, plus_func, plus=2)
    assert np.array_equal(task.trial['outer']['inner1'], np.array([3.5, 4.5, 5.5]))
    assert np.array_equal(task.trial['outer']['inner2'], np.array([4.5, 5.5, 6.5]))

def test_task_convert_type():

    task = TaskBase()
    task.trial['stuff'] = '1'
    task.convert_type('trial', 'stuff', int)
    assert isinstance(task.trial['stuff'], int)
    assert task.trial['stuff'] == 1

def test_task_convert_to_array():

    task = TaskBase()
    task.trial['stuff'] = [1, 2, 3]
    task.convert_to_array('trial', 'stuff', int)
    assert isinstance(task.trial['stuff'], np.ndarray)
    assert task.trial['stuff'].dtype == 'int64'
    assert np.array_equal(task.trial['stuff'], np.array([1, 2, 3]))

    task = TaskBase()
    task.trial['outer'] = {}
    task.trial['outer']['inner1'] = [1.5, 2.5, 3.5]
    task.trial['outer']['inner2'] = [2.5, 3.5, 4.5]
    task.convert_to_array('trial', {'outer' : ['inner1', 'inner2']}, float)
    for label in ['inner1', 'inner2']:
        assert isinstance(task.trial['outer'][label], np.ndarray)
        assert task.trial['outer'][label].dtype == 'float64'
    assert np.array_equal(task.trial['outer']['inner1'], np.array([1.5, 2.5, 3.5]))
    assert np.array_equal(task.trial['outer']['inner2'], np.array([2.5, 3.5, 4.5]))

def test_task_get_trial():

    # Check without using subfield
    task = TaskBase()
    trial_data = {'a' : [1, 2], 'b' : [True, False]}
    task.trial = trial_data
    assert task.get_trial(0) == {'a' : 1, 'b' : True}
    assert task.get_trial(1) == {'a' : 2, 'b' : False}

    # Check using subfield
    task = TaskBase()
    trial_data = {'top' : ['a1', 'a2'],
                  'field' : {'a' : [1, 2], 'b' : [True, False]}}
    task.trial = trial_data
    assert task.get_trial(0, 'field') == {'a' : 1, 'b' : True}
    assert task.get_trial(1, 'field') == {'a' : 2, 'b' : False}

def test_task_update_time_offset():

    task = TaskBase()
    task.trial['sub1'] = {}
    task.trial['sub2'] = {}
    task.custom = {}

    task.session['start_time'] = 10
    task.session['end_time'] = 40
    task.position['time'] = np.array([15, 25, 35])
    task.trial['sub1']['happen_time'] = np.array([11, 21, 31])
    task.trial['sub2']['response_time'] = np.array([19, 29, 39])
    task.custom['time'] = np.array([12, 22, 32])

    task.update_time('offset', offset=10)
    assert task.session['start_time'] == 0
    assert task.session['end_time'] == 30
    assert np.array_equal(task.position['time'], np.array([5, 15, 25]))
    assert np.array_equal(task.trial['sub1']['happen_time'], np.array([1, 11, 21]))
    assert np.array_equal(task.trial['sub2']['response_time'], np.array([9, 19, 29]))
    assert np.array_equal(task.custom['time'], np.array([2, 12, 22]))

def test_task_update_time_change_units():

    task = TaskBase()
    task.trial['sub1'] = {}
    task.trial['sub2'] = {}
    task.custom = {}

    task.session['start_time'] = 0
    task.session['end_time'] = 3000
    task.position['time'] = np.array([500, 1500, 2500])
    task.trial['sub1']['happen_time'] = np.array([100, 1100, 2100])
    task.trial['sub2']['response_time'] = np.array([900, 1900, 2900])
    task.custom['time'] = np.array([200, 1200, 2200])

    task.update_time('change_units', value=100, operation='divide')
    assert task.session['start_time'] == 0
    assert task.session['end_time'] == 30
    assert np.array_equal(task.position['time'], np.array([5, 15, 25]))
    assert np.array_equal(task.trial['sub1']['happen_time'], np.array([1, 11, 21]))
    assert np.array_equal(task.trial['sub2']['response_time'], np.array([9, 19, 29]))
    assert np.array_equal(task.custom['time'], np.array([2, 12, 22]))

def test_task_update_time_custom():

    def custom_func(data, mult):
        return data * mult

    task = TaskBase()
    task.trial['sub1'] = {}
    task.trial['sub2'] = {}
    task.custom = {}

    task.session['start_time'] = 0
    task.session['end_time'] = 30
    task.position['time'] = np.array([5, 15, 25])
    task.trial['sub1']['happen_time'] = np.array([1, 11, 21])
    task.trial['sub2']['response_time'] = np.array([9, 19, 29])
    task.custom['time'] = np.array([2, 12, 22])

    task.update_time(custom_func, mult=2)
    assert task.session['start_time'] == 0
    assert task.session['end_time'] == 60
    assert np.array_equal(task.position['time'], np.array([10, 30, 50]))
    assert np.array_equal(task.trial['sub1']['happen_time'], np.array([2, 22, 42]))
    assert np.array_equal(task.trial['sub2']['response_time'], np.array([18, 38, 58]))
    assert np.array_equal(task.custom['time'], np.array([4, 24, 44]))

def test_task_update_time_apply_type():

    task = TaskBase()
    task.session['start_time'] = 10.
    task.position['time'] = [15, 25, 35]

    task.update_time(convert_to_array, apply_type=list, dtype=float)
    assert isinstance(task.session['start_time'], float)
    assert task.session['start_time'] == 10.
    assert isinstance(task.position['time'], np.ndarray)
    assert np.array_equal(task.position['time'], np.array([15, 25, 35]))

def test_task_to_dict(ttask_full):

    odict = ttask_full.to_dict()
    assert isinstance(odict, dict)

def test_task_to_dataframe(ttask_full):

    df = ttask_full.to_dataframe('trial')
    assert isinstance(df, pd.DataFrame)
