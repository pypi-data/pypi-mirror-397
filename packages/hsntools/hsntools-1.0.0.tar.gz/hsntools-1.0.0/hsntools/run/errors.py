"""Helper functions for running procedures."""

import traceback

from hsntools.io.files import save_txt
from hsntools.run.log import print_status

###################################################################################################
###################################################################################################

def catch_error(proceed, name, path, verbose=True, message=None, print_level=0):
    """Catch a raised error, with the option to save an error log and proceed.

    Parameters
    ----------
    proceed : bool
        Whether to proceed.
        If True, the error is saved out, and execution proceeds.
        If False, the error is raised.
    name : str
        Name of the file that has an error.
    path : str or Path
        Path location to save out the error log
    verbose : bool, optional, default: True
        Whether to print a log of the
    message : str, optional
        Message to print out.
    print_level : {0, 1, 2}
        Print level for the printed message. Only used if `verbose` is True.

    Raises
    ------
    Error
        If proceed is False, then the error is re-raised.

    Notes
    -----
    This function assumes an error has just been raised and should be used within a try/except.
    """

    if not proceed:
        raise

    if not message:
        message = 'ISSUE WITH FILE: \t{}'
    message = message.format(name) if '{}' in message else message

    print_status(verbose, message, print_level)
    save_txt(traceback.format_exc(), name, folder=path)
