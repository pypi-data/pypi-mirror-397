"""Tools for status logging."""

###################################################################################################
###################################################################################################

def print_status(verbose, message, level=1):
    """Print a status update.

    Parameters
    ----------
    verbose : bool
        Whether to print.
    message : str
        Text to print out.
    level : int
        Indentation level.
    """

    if verbose:
        print('\t' * level + message)
