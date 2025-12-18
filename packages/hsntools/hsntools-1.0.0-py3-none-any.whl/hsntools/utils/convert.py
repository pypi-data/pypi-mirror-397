"""Utility functions for converting data types."""

import numpy as np

###################################################################################################
###################################################################################################

def convert_str_to_bool(string):
    """Convert a string to a boolean.

    Parameters
    ----------
    string : {'True', 'False'}
        String to convert to boolean.

    Returns
    -------
    bool
        Boolean represetation of the string.
    """

    assert string.lower() in ['true', 'false']
    return string.lower() == 'true'


def convert_strlist_to_bool(lst):
    """Convert a list of strings to a list of boolean.

    Parameters
    ----------
    lst : list of str
        List of strings to convert to boolean.

    Returns
    -------
    list of bool
        List with elements converted to boolean.
    """

    return [convert_str_to_bool(el) for el in lst]


def convert_type(variable, dtype):
    """Convert type of a given variable.

    Parameters
    ----------
    variable
        Variable to type cast.
    dtype : type
        Type to cast to.

    Returns
    -------
    out
        Typecast `value`, with type `dtype`.
    """

    out = dtype(variable)

    return out


def convert_to_array(data, dtype):
    """Convert to an array of specified data type.

    Parameters
    ----------
    data : array_like
        Data to cast to an array.
    dtype : str
        Data type to cast the array.

    Returns
    -------
    array : np.ndarray
        Data, converted to array.
    """

    array = np.array(data).astype(dtype)

    return array
