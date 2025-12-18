"""Utility functions for checking and cleaning variables."""

import numpy as np

###################################################################################################
###################################################################################################

def is_empty(var):
    """Check if a variable is empty, across multiple possible types.

    Parameters
    ----------
    var
        Variable to test for whether it's empty.

    Returns
    -------
    empty : bool
        Indicates whether the given variable is empty.
    """

    if var is None:
        out = True
    elif isinstance(var, (int, float, str)):
        out = not bool(var)
    elif isinstance(var, (list, tuple)):
        out = not bool(len(var))
    elif isinstance(var, np.ndarray):
        out = not var.any()
    else:
        msg = 'Empty check for given type {} not implemented.'.format(str(type(var)))
        raise NotImplementedError(msg)

    return out


def is_type(var, var_type):
    """Check is a variable is of the given type(s).

    Parameters
    ----------
    var
        Variable to test for type match.
    var_type : type or None
        Type to test against.
        If None, then returns True (no type check).

    Returns
    -------
    type_match : bool
        Indicates whether the given variable is matches the given type.
    """

    # If type not provided, return True, otherwise return whether is selected type
    if not var_type:
        type_match = True
    else:
        type_match = isinstance(var, var_type)

    return type_match


def check_str_contents(str_to_check, contents):
    """Check whether a given string has specified contents.

    Parameters
    ----------
    str_to_check : str
        String to check contents.
    contents : str or list of str
        String(s) to check whether they are contained in `str_to_check`.

    Returns
    -------
    has_contents : bool
        Indicates whether the given string contains the provided content(s).
    """

    contents = [contents] if isinstance(contents, str) else contents

    has_contents = False
    for content in contents:
        if content in str_to_check:
            has_contents = True
            break

    return has_contents


def clean_strings(lst):
    """Helper function to clean a list of string values for adding to NWB.

    Parameters
    ----------
    lst : list
        A list of (mostly) strings to be prepped for adding to NWB.

    Returns
    -------
    list of str
        Cleaned list.

    Notes
    -----
    Each element is checked:

    - str types and made lower case and kept
    - any other type is replaced with 'none' (as a string)
    - the goal is to replace Python nan or None types for empty cells
    """

    return [val.lower() if isinstance(val, str) else 'none' for val in lst]
