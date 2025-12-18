"""File I/O for basic file types."""

import json

from hsntools.io.utils import check_ext, check_folder
from hsntools.modutils.dependencies import safe_import, check_dependency

sio = safe_import('.io', 'scipy')
pd = safe_import('pandas')
mat73 = safe_import('mat73')

###################################################################################################
###################################################################################################

def save_txt(text, file_name, folder=None):
    """Save out text to a txt file.

    Parameters
    ----------
    text : str
        Text to save out to a txt file.
    file_name : str
        File name to give the saved out txt file.
    folder : str or Path, optional
        Folder to save out to.
    """

    with open(check_ext(check_folder(file_name, folder), '.txt'), 'w') as txt_file:
        txt_file.write(text)


def load_txt(file_name, folder=None):
    """Load text from a txt file.

    Parameters
    ----------
    file_name : str
        File name of the file to load.
    folder : str or Path, optional
        Folder to load from.

    Returns
    -------
    text : str
        Loaded text from the txt file.
    """

    with open(check_ext(check_folder(file_name, folder), '.txt')) as txt_file:
        text = txt_file.readlines()

    return text


def save_json(data, file_name, folder=None):
    """Save out a dictionary of data to a JSON file.

    Parameters
    ----------
    data : dict
        Data to save out to a JSON file.
    file_name : str
        File name to give the saved out json file.
    folder : str or Path, optional
        Folder to save out to.
    """

    with open(check_ext(check_folder(file_name, folder), '.json'), 'w') as json_file:
        json.dump(data, json_file)


def load_json(file_name, folder=None):
    """Load from a JSON file.

    Parameters
    ----------
    file_name : str
        File name of the file to load.
    folder : str or Path, optional
        Folder to load from.

    Returns
    -------
    data : dict
        Loaded data from the JSON file.
    """

    with open(check_ext(check_folder(file_name, folder), '.json')) as json_file:
        data = json.load(json_file)

    return data


def save_jsonlines(data, file_name, folder=None):
    """Save out data to a JSONlines file.

    Parameters
    ----------
    data : list of dict
        Data to save out to a JSONlines file.
    file_name : str
        File name to give the saved out json file.
    folder : str or Path, optional
        Folder to save out to.
    """

    with open(check_ext(check_folder(file_name, folder), '.json'), 'a') as jsonlines_file:
        for cur_data in data:
            json.dump(cur_data, jsonlines_file)
            jsonlines_file.write('\n')


def load_jsonlines(file_name, folder=None):
    """Load from a JSON lines file.

    Parameters
    ----------
    file_name : str
        File name of the file to load.
    folder : str or Path, optional
        Folder to load from.

    Returns
    -------
    data : dict
        Loaded data from the JSONlines file.
    """

    all_data = {}
    with open(check_ext(check_folder(file_name, folder), '.json'), 'r') as jsonlines_file:
        for line in jsonlines_file:
            line_data = json.loads(line)
            key = list(line_data.keys())[0]
            all_data[key] = line_data[key]

    return all_data


@check_dependency(pd, 'pandas')
def load_excel(file_name, folder, sheet=0):
    """Load an excel (xlsx) file.

    Parameters
    ----------
    file_name : str
        File name of the file to load.
    folder : str or Path, optional
        Folder to load from.

    Returns
    -------
    pd.DataFrame
        Loaded data from the excel file.
    """

    return pd.read_excel(check_ext(check_folder(file_name, folder), '.xlsx'),
                         engine='openpyxl', sheet_name=sheet)


def load_matfile(file_name, folder=None, version=None, **kwargs):
    """Load a .mat file.

    Parameters
    ----------
    file_name : str
        File name of the file to load.
    folder : str or Path, optional
        Folder to load from.
    version : {'scipy', 'mat73'}
        Which matfile load function to use:
            'scipy' : uses `scipy.io.loadmat`, works for matfiles older than v7.3
            'mat73' : uses `mat73.loadmat`, works for matfile v7.3 files
        If not specified, tries both.
    **kwargs
        Additional keywork arguments to pass into to matfile load function.

    Returns
    -------
    dict
        Loaded data from the matfile.
    """

    loaders = {
        'scipy' : _load_matfile_scipy,
        'mat73' : _load_matfile73,
    }

    file_path = check_ext(check_folder(file_name, folder), '.mat')

    if version:
        return loaders[version](file_path, **kwargs)
    else:
        try:
            _load_matfile_scipy(file_path, **kwargs)
        except NotImplementedError:
            return _load_matfile73(file_path, **kwargs)


@check_dependency(sio, 'scipy')
def _load_matfile_scipy(file_path, **kwargs):
    """Load matfile - scipy version."""

    return sio.loadmat(file_path, **kwargs)


@check_dependency(mat73, 'mat73')
def _load_matfile73(file_path, **kwargs):
    """Load matfile - mat73 version."""

    return mat73.loadmat(file_path, **kwargs)
