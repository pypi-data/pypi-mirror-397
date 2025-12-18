"""File I/O for HDF5 files, including context managers.

Functionality in this file requires the `h5py` module: https://github.com/h5py/h5py
"""

from contextlib import contextmanager

from hsntools.io.utils import check_ext, check_folder
from hsntools.modutils.dependencies import safe_import, check_dependency

h5py = safe_import('h5py')

###################################################################################################
###################################################################################################

@check_dependency(h5py, 'h5py')
def access_h5file(file_name, folder=None, mode='r', ext='.h5', **kwargs):
    """Access a HDF5 file.

    Parameters
    ----------
    file_name : str
        File name of the h5file to open.
    folder : str or Path, optional
        Folder to open the file from.
    mode : {'r', 'r+', 'w', 'w-', 'x', 'a'}
        Mode to access file. See h5py.File for details.
    ext : str, optional default: '.h5'
        The extension to check and use for the file.
    **kwargs
        Additional keyword arguments to pass into h5py.File.

    Returns
    -------
    h5file
        Open h5file object.

    Notes
    -----
    This function is a wrapper for `h5py.File`.
    """

    h5file = h5py.File(check_ext(check_folder(file_name, folder), ext), mode, **kwargs)

    return h5file


@contextmanager
@check_dependency(h5py, 'h5py')
def open_h5file(file_name, folder=None, mode='r', ext='.h5', **kwargs):
    """Context manager to open a HDF5 file.

    Parameters
    ----------
    file_name : str
        File name of the h5file to open.
    folder : str or Path, optional
        Folder to open the file from.
    ext : str, optional default: '.h5'
        The extension to check and use for the file.
    **kwargs
        Additional keyword arguments to pass into h5py.File.

    Yields
    ------
    h5file
        Open h5file object.

    Notes
    -----
    This function is a wrapper for `h5py.File`, creating a context manager.
    """

    h5file = access_h5file(file_name, folder, mode, ext, **kwargs)

    try:
        yield h5file
    finally:
        h5file.close()


@check_dependency(h5py, 'h5py')
def save_to_h5file(data, file_name, folder=None, ext='.h5', **kwargs):
    """Save data to a HDF5 file.

    Parameters
    ----------
    data : dict
        Dictionary of data to save to the HDF5 file.
        Each key will be used as the HDF5 dataset label.
        Each set of values will be saved as the HDF5 dataset data.
    file_name : str
        File name of the h5file to save to.
    folder : str or Path, optional
        Folder to save the file to.
    ext : str, optional default: '.h5'
        The extension to check and use for the file.
    **kwargs
        Additional keyword arguments to pass into h5py.File.
    """

    with open_h5file(file_name, folder, mode='w', ext=ext, **kwargs) as h5file:
        for label, values in data.items():
            h5file.create_dataset(label, data=values)


@check_dependency(h5py, 'h5py')
def load_from_h5file(fields, file_name, folder=None, ext='.h5', **kwargs):
    """Load one or more specified field(s) from a HDF5 file.

    Parameters
    ----------
    field : str or list of str
        Name(s) of the field to load from the HDF5 file.
    file_name : str
        File name of the h5file to open.
    folder : str or Path, optional
        Folder to open the file from.
    ext : str, optional default: '.h5'
        The extension to check and use for the file.
    **kwargs
        Additional keyword arguments to pass into h5py.File.

    Returns
    -------
    data : dict
        Loaded data field from the file.
        Each key is the field label, each set of values the loaded data.
    """

    fields = [fields] if isinstance(fields, str) else fields

    outputs = {}
    with open_h5file(file_name, folder, mode='r', ext=ext, **kwargs) as h5file:
        for field in fields:
            if h5file[field].size == 1:
                outputs[field] = h5file[field][()]
            else:
                outputs[field] = h5file[field][:]

    return outputs
