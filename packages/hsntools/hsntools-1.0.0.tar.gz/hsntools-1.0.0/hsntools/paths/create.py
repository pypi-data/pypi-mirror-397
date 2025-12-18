"""Functions for creating directory structures."""

import os
from pathlib import Path
from copy import deepcopy

from hsntools.run.log import print_status
from hsntools.paths.defaults import PROJECT_FOLDERS, SUBJECT_FOLDERS, SESSION_FOLDERS

###################################################################################################
###################################################################################################

def make_folder(path):
    """Make a folder, if it does not already exist.

    Parameters
    ----------
    path : str of Path
        Path to the folder to make.
    """

    if not os.path.exists(path):
        os.mkdir(path)


def create_project_directory(base_path, project, project_folders=PROJECT_FOLDERS, verbose=True):
    """Create the folder structure for one or more projects.

    Parameters
    ----------
    base_path : str or Path
        The path to the folder where to put the project.
    project : str or list
        The project name(s).
        If list, should be a list of project names, each which will be created.
    project_folders : list, optional
        List of sub-folders to initialize in the project folder.
    verbose : bool, optional, default: True
        Whether to print out information.
    """

    if isinstance(project, list):

        for cproject in project:
            create_project_directory(base_path, cproject, project_folders, verbose)

    else:

        base_path = Path(base_path)
        print_status(verbose, 'Creating project directory...', 0)
        print_status(verbose, 'Path: {}'.format(base_path / project), 1)

        make_folder(base_path / project)
        for subfolder in project_folders:
            make_folder(base_path / project / subfolder)


def create_subject_directory(project_path, subject, experiments=None,
                             subject_folders=SUBJECT_FOLDERS, recordings_name='recordings',
                             verbose=True):
    """Create the folder structure for one or more subjects.

    Parameters
    ----------
    project_path : str or Path
        The path to the project folder.
    subject : str or list
        The subject code(s).
        If list, should be a list of subject codes, each which will be created.
    experiments : str or list, optional
        Experiment name(s) to initialize in the subject(s) folder(s).
    subject_folders : list, optional
        List of sub-folders to initialize in the subject folder.
    recordings_name : str, optional
        The name of the subfolder (within `project_path`) to store recordings.
    verbose : bool, optional, default: True
        Whether to print out information.
    """

    if isinstance(subject, list):

        for csubject in subject:
            create_subject_directory(project_path, csubject, experiments,
                                     subject_folders, recordings_name, verbose)

    else:

        recordings_path = Path(project_path) / recordings_name

        print_status(verbose, 'Creating subject directory...', 0)
        print_status(verbose, 'Path: {}'.format(recordings_path / subject), 1)

        make_folder(recordings_path)
        make_folder(recordings_path / subject)

        all_subject_folders = deepcopy(subject_folders)
        if experiments:
            experiments = [experiments] if isinstance(experiments, str) else experiments
            all_subject_folders = all_subject_folders + experiments
        for subfolder in all_subject_folders:
            make_folder(recordings_path / subject / subfolder)


def create_session_directory(project_path, subject, experiment, session,
                             recordings_name='recordings', session_folders=SESSION_FOLDERS,
                             verbose=True):
    """Create the folder structure for one or more sessions of data.

    Parameters
    ----------
    project_path : str or Path
        The path to the project folder.
    subject : str or list
        The subject code(s) to create the session folders within.
    experiment : str
        Experiment name to create the session folders within.
    session : str or int or list
        The session label(s) to create the folder structure for.
        Can be an integer index, or a string, for example `session_0`.
        If list, should be a list of str or int to create multiple session folders.
    recordings_name : str, optional
        The name of the subfolder (within `project_path`) to store recordings.
    session_folders : dict, optional
        Defines the folder names to initialize as part of the session folder.
        Each key defines a sub-directory within the `session` folder.
        Each set of values is a list of folder names for within each sub-directory.
    verbose : bool, optional, default: True
        Whether to print out information.
    """

    if isinstance(subject, list):

        for csubject in subject:
            create_session_directory(project_path, csubject, experiment, session,
                                     recordings_name, session_folders, verbose)

    else:

        if isinstance(session, list):

            for csession in session:
                create_session_directory(project_path, subject, experiment, csession,
                                         recordings_name, session_folders, verbose)

        else:

            recordings_path = Path(project_path) / recordings_name

            session = 'session_' + str(session) if 'session' not in str(session) else session

            print_status(verbose, 'Creating session directory...', 0)
            print_status(verbose,
                         'Path: {}'.format(recordings_path / subject / experiment / session), 1)

            create_subject_directory(project_path, subject, experiments=[experiment],
                                     recordings_name=recordings_name, verbose=False)

            make_folder(recordings_path / subject / experiment / session)
            for subdir, subfolders in session_folders.items():
                make_folder(recordings_path / subject / experiment / session / subdir)
                for subfolder in subfolders:
                    make_folder(recordings_path / subject / experiment / session / subdir / subfolder)
