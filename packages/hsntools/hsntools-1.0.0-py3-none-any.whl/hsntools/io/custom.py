"""File I/O for custom files."""

import pickle

import yaml

from hsntools.io.utils import check_ext, check_folder

###################################################################################################
###################################################################################################

#### CONFIG FILES

def save_config(cdict, file_name, folder=None):
    """Save out a config file.

    Parameters
    ----------
    cdict : dict
        Dictionary of information to save to the config file.
    file_name : str
        File name to give the saved out config file.
    folder : str or Path, optional
        Folder to save the config file to.
    """

    with open(check_ext(check_folder(file_name, folder), '.yaml'), 'w') as file:
        yaml.dump(cdict, file)


def load_config(file_name, folder=None):
    """Load an individual config file.

    Parameters
    ----------
    file_name : str
        Name of the config file to load.
    folder : str or Path, optional
        Folder to load the config file from.

    Returns
    -------
    data : dict
        Information from the loaded config file.
    """

    with open(check_ext(check_folder(file_name, folder), '.yaml'), 'r') as fobj:
        data = yaml.safe_load(fobj)

    return data


def load_configs(files, folder=None):
    """Load all configs together.

    Parameters
    ----------
    files : list of str
        Names of all the config files to load.
    folder : str or Path, optional
        Folder to load the config files from.

    Returns
    -------
    configs : dict
        Information from the config files.
    """

    configs = {}
    for file in files:
        label = file.split('_')[0]
        configs[label] = load_config(file, folder=folder)

    return configs


### CUSTOM OBJECTS

def save_object(custom_object, file_name, folder=None):
    """Save a custom object.

    Parameters
    ----------
    custom_object : Task or Electrodes
        Object to save out.
    file_name : str
        File name to give the saved out object.
    folder : str or Path, optional
        Folder to save out to.

    Notes
    -----
    Custom objects are saved and loaded as pickle files.
    """

    ext = '.' + str(type(custom_object)).split('.')[-1].strip("'>").lower()
    if 'task' in ext:
        ext = '.task'

    with open(check_ext(check_folder(file_name, folder), ext), 'wb') as fobj:
        pickle.dump(custom_object, fobj)


def load_object(file_name, folder=None):
    """Load a custom object.

    Parameters
    ----------
    file_name : str
        File name of the file to load.
    folder : str or Path, optional
        Folder to load from.

    Returns
    -------
    custom_object
        Loaded task object.

    Notes
    -----
    Custom objects are saved and loaded as pickle files.
    """

    with open(check_folder(file_name, folder), 'rb') as load_obj:
        custom_object = pickle.load(load_obj)

    return custom_object
