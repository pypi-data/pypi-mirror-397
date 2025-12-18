"""Functionality for working with dates."""

from datetime import datetime
from dateutil.tz import tzlocal

###################################################################################################
###################################################################################################

def get_current_date(tz=None):
    """Get the current datetime.

    Parameters
    ----------
    tz : dateutil.tz.tz, optional
        Timezone information. If not provided, defaults to the local time zone.

    Returns
    -------
    date : datetime.datetime
        The current date information.
    """

    if not tz:
        tz = tzlocal()

    date = datetime.now(tzlocal())

    return date


def convert_time_to_date(timestamp, tz=None):
    """Convert a time value to a datetime date.

    Parameters
    ----------
    timestamp : float
        Timestamp value to convert.
    tz : dateutil.tz.tz, optional
        Timezone information. If not provided, defaults to the local time zone.

    Returns
    -------
    date : datetime.datetime
        Date corresponding to the given timestamp.
    """

    if not tz:
        tz = tzlocal()

    date = datetime.fromtimestamp(timestamp, tz=tz)

    return date
