"""File IO for loading collections of files together."""

import pathlib

from hsntools.io.files import load_json
from hsntools.io.utils import get_files
from hsntools.modutils.dependencies import safe_import, check_dependency

pd = safe_import('pandas')

###################################################################################################
###################################################################################################

@check_dependency(pd, 'pandas')
def load_jsons_to_df(files, folder=None):
    """Load a collection of JSON files into a dataframe.

    Parameters
    ----------
    files : list of str or str or Path
        If list, should be a list of file names to load.
        If str or Path, should be a folder name, from which all JSON files will be loaded.
    folder : str or Path, optional
        Folder location to load the files from.
        Only used if `files` is a list of str.

    Returns
    -------
    df : pd.DataFrame
        A dataframe containing the data from the JSON files.
    """

    if isinstance(files, (str, pathlib.PosixPath)):
        files = get_files(folder, select='json')

    file_data = [load_json(file, folder=folder) for file in files]

    df = pd.DataFrame(file_data)

    return df
