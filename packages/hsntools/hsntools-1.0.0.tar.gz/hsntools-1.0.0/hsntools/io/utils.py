"""Utilities related to file I/O."""

import os

###################################################################################################
###################################################################################################

def check_ext(file_name, ext):
    """Check the extension for a file name, and add if missing.

    Parameters
    ----------
    file_name : str
        The name of the file.
    ext : str
        The extension to check and add.

    Returns
    -------
    str
        File name with the extension added.
    """

    return file_name + ext if not file_name.endswith(ext) else file_name


def drop_ext(file_name):
    """Drop the extension from a file name.

    Parameters
    ----------
    file_name : str
        File name, potentially including a file extension.

    Returns
    -------
    file_name : str
        File name, without the file extension.
    """

    return file_name.split('.')[0]


def check_folder(file_name, folder):
    """Check a file name, adding folder path if needed.

    Parameters
    ----------
    file_name : str
        The name of the file.
    folder : str or Path, optional
        Folder location of the file.

    Returns
    -------
    str
        Full path of the file.
    """

    return os.path.join(folder, file_name) if folder else file_name


def drop_hidden_files(files):
    """Clean hidden files from a list of files.

    Parameters
    ----------
    files : list of str
        List of file names.

    Returns
    -------
    list of str
        List of file names with hidden files dropped.
    """

    return [file for file in files if file[0] != '.']


def drop_file_extensions(files):
    """Drop the file extensions from a list of file names.

    Parameters
    ----------
    files : list of str
        List of file names.

    Returns
    -------
    list of str
        List of file names with extensions dropped.
    """

    return [drop_ext(file) for file in files]


def ignore_files(files, ignore):
    """Ignore files based on a search term of interest.

    Parameters
    ----------
    files : list of str
        List of file names.
    ignore : str
        String to use to drop files from list.

    Returns
    -------
    list of str
        List of file names with ignored files dropped.
    """

    return [file for file in files if ignore not in file]


def select_files(files, search):
    """Select files based on a search term of interest.

    Parameters
    ----------
    files : list of str
        List of file names.
    search : str
        String to use to keep files.

    Returns
    -------
    list of str
        List of file names with selected files kept.
    """

    return [file for file in files if search in file]


def sort_files(files):
    """Sort a list of file names.

    Parameters
    ----------
    files : list of str
        List of file names.

    Returns
    -------
    list of str
        Sorted list of file names.
    """

    return sorted(files)


def make_session_name(subject, experiment, session):
    """Create a standardized session name.

    Parameters
    ----------
    subject : str
        The subject label.
    experiment : str, optional
        Name of the experiment.
    session : str or int
        The session number.
        Can be an integer index, or a string, for example `session_0`.
    add_ext : bool, optional, default: False
        Whether to add the NWB extension to the file name.

    Returns
    -------
    session_name : str
        The session name.

    Notes
    -----
    The standard session name is structured as: 'EXPERIMENT_SUBJECT_session_#'
    Note that this is a flip of the experiment / subject order in the path layout.
    """

    session = 'session_' + str(session) if 'session' not in str(session) else session
    session_name = '_'.join([experiment, subject, session])

    return session_name


def make_file_list(experiment, files, ext=None):
    """Make a list of subject files.

    Parameters
    ----------
    experiment : str
        Name of the experiment.
    files : dict
        Collection of files per subject.
    ext : str, optional
        Extension name to add to the file list.

    Returns
    -------
    file_lst : list of str
        List of all subject files.
    """

    file_list = []
    for subject, sessions in files.items():
        for session in sessions:
            file_name = '_'.join([experiment, subject, session])
            file_name = check_ext(file_name, ext) if ext else file_name
            file_list.append(file_name)

    return file_list


def file_in_list(file_name, file_list, drop_extensions=True):
    """Check whether a given file name is in a list of file names.

    Parameters
    ----------
    file_name : str
        File name.
    file_list : list of str
        List of file names.
    drop_extensions : bool, optional, default: True
        Whether to drop any extensions before doing the comparison.

    Returns
    -------
    bool
        Indicator of whether the file name is in the list of file names.
    """

    if drop_extensions:
        file_name = drop_ext(file_name)
        file_list = drop_file_extensions(file_list)

    output = False
    if file_name in file_list:
        output = True

    return output


def missing_files(file_list, compare):
    """Check for missing files - those that are in a given list but not in a comparison list.

    Parameters
    ----------
    file_list : list of str
        List of files to check.
    compare : list of str
        List of files to compare to.

    Returns
    -------
    list of str
        Any files from `file_list` that are not in `compare`.
    """

    return list(set(file_list) - set(compare))


def get_files(folder, select=None, ignore=None, drop_hidden=True, sort=True, drop_extensions=False):
    """Get a list of files from a specified folder.

    Parameters
    ----------
    folder : str or Path
        Name of the folder to get the list of files from.
    select : str, optional
        A search string to use to select files.
    ignore : str, optional
        A search string to use to drop files.
    drop_hidden : bool, optional, default: True
        Whether to drop hidden files from the list.
    sort : bool, optional, default: True
        Whether to sort the list of file names.
    drop_extensions : bool, optional, default: False
        Whether the drop the file extensions from the returned file list.

    Returns
    -------
    list of str
        A list of files from the folder.
    """

    files = os.listdir(folder)

    # If requested, drop any hidden files (leading .'s)
    if drop_hidden:
        files = drop_hidden_files(files)

    # If requested, filter files to those that containing given search terms
    if select:
        files = select_files(files, select)

    # If requested, filter files to ignore any containing given search terms
    if ignore:
        files = ignore_files(files, ignore)

    # If requested, sort the list of files
    if sort:
        files = sort_files(files)

    if drop_extensions:
        files = drop_file_extensions(files)

    return files


def get_subfolders(folder, select=None, ignore=None):
    """Get a list of sub-folders from a given folder.

    Parameters
    ----------
    folder : str
        Name of the folder to get the list of sub-folders from.

    Returns
    -------
    subfolders : list of str
        A list of sub-folders from the folder.
    """

    subfolders = []
    for entry in os.scandir(folder):
        if entry.is_dir():
            subfolders.append(entry.name)

    if select:
        subfolders = select_files(subfolders, select)
    if ignore:
        subfolders = ignore_files(subfolders, ignore)

    return subfolders
