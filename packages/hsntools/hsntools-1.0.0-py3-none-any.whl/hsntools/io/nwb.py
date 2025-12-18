"""Helper utilities for validating NWB files.

Functionality in this file requires the `pynwb` module:
https://github.com/NeurodataWithoutBorders/pynwb
"""

from hsntools.io.utils import check_ext, check_folder, make_session_name
from hsntools.modutils.dependencies import safe_import, check_dependency

pynwb = safe_import('pynwb')

###################################################################################################
###################################################################################################

@check_dependency(pynwb, 'pynwb')
def save_nwbfile(nwbfile, file_name, folder=None):
    """Save out an NWB file.

    Parameters
    ----------
    file_name : str or dict
        The file name to load.
        If dict, is passed into `make_session_name` to create the file name.
    folder : str or Path, optional
        The folder to load the file from.
    """

    if isinstance(file_name, dict):
        file_name = make_session_name(**file_name)

    with pynwb.NWBHDF5IO(check_ext(check_folder(file_name, folder), '.nwb'), 'w') as io:
        io.write(nwbfile)


@check_dependency(pynwb, 'pynwb')
def load_nwbfile(file_name, folder=None, return_io=False):
    """Load an NWB file.

    Parameters
    ----------
    file_name : str or dict
        The file name to load.
        If dict, is passed into `make_session_name` to create the file name.
    folder : str or Path, optional
        The folder to load the file from.
    return_io : bool, optional, default: False
        Whether to return the pynwb IO object.

    Returns
    -------
    nwbfile : pynwb.file.NWBFile
        The NWB file object.
    io : pynwb.NWBHDF5IO
        The IO object for managing the file status.
        Only returned if `return_io` is True.
    """

    if isinstance(file_name, dict):
        file_name = make_session_name(**file_name)

    io = pynwb.NWBHDF5IO(check_ext(check_folder(file_name, folder), '.nwb'), 'r')
    nwbfile = io.read()

    if return_io:
        return nwbfile, io
    else:
        return nwbfile


@check_dependency(pynwb, 'pynwb')
def validate_nwbfile(file_name, folder=None, raise_error=True, verbose=False):
    """Validate a NWB file.

    Parameters
    ----------
    file_name : str or Path
        Name of the NWB file to validate.
    folder : str or Path, optional
        Name of the folder where the file is located.
    raise_error : boolean, optional, default: True
        Whether to raise an error if the NWB file fails validation.
    verbose : boolean, optional, default: True
        Whether to print out information about NWB validation.

    Returns
    -------
    errors : list or None
        A list of errors if any were found, None if no errors were found.

    Raises
    ------
    ValueError
        If there is an error in the NWB file. Only raised if `raise_error` is True.
    """

    file_name = check_folder(check_ext(file_name, '.nwb'), folder)
    with pynwb.NWBHDF5IO(file_name, 'r') as nwb_file:
        errors = pynwb.validate(nwb_file)

    if verbose:

        if errors:
            print('NWB errors: ')
            for error in errors:
                print('\t', error)
        else:
            print('NWB validation successful.')

    if raise_error and errors:

        raise ValueError('There is an issue with the NWB file.')

    return errors if errors else None
