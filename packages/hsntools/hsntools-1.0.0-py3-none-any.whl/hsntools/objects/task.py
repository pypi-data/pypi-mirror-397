"""Base task class."""

from copy import deepcopy

from hsntools.timestamps.align import predict_times
from hsntools.timestamps.update import offset_time, change_time_units
from hsntools.utils.checks import is_empty, is_type
from hsntools.utils.convert import convert_type, convert_to_array
from hsntools.modutils.dependencies import safe_import, check_dependency

pd = safe_import('pandas')

###################################################################################################
###################################################################################################

TIME_UPDATES = {
    'offset' : offset_time,
    'change_units' : change_time_units,
    'predict_times' : predict_times,
}

class TaskBase():
    """Base object for collecting task information."""

    def __init__(self):
        """Initialize TaskBase object."""

        # Define information about the status and info attached to the task object
        self.status = {
            'time_aligned' : False,
            'time_reset' : False,
        }
        self.info = {
            'time_offset' : None,
        }

        # Metadata - subject / session information
        self.meta = {
            'experiment' : None,
            'subject' : None,
            'session' : None,
        }

        # Experiment information
        self.experiment = {
            'version' : {
                'label' : None,
                'number' : None,
                },
            'language' : None,
        }

        # Environment information
        self.environment = {}

        # Session information
        self.session = {
            'start_time' : None,
            'stop_time' : None,
        }

        # Synchronization information
        self.sync = {
            # Define synchronization approach
            'approach' : None,
            # Synchronization pulses
            'neural' : [],
            'behavioral' : [],
            # Synchronization alignment
            'alignment' : {
                'intercept' : None,
                'coef' : None,
                'score' : None,
            }
        }

        # Position related information
        self.position = {
            'time' : [],
            'x' : [],
            'y' : [],
            'z' : [],
            'speed' : [],
        }

        # Head direction information
        self.head_direction = {
            'time' : [],
            'degrees' : [],
        }

        # Information about timing of task phases
        self.phase_times = {}

        # Stimulus information
        self.stimuli = {}

        # Trial information
        self.trial = {
            'trial' : [],
            'type' : [],
            'start_time' : [],
            'stop_time' : [],
        }

        # Response information
        self.responses = {}


    def _check_field(self, field):
        """Check that a requested field is defined in the object.

        Parameters
        ----------
        field : str
            Which field to check.

        Raises
        ------
        AssertionError
            If the requested field is not part of the object.
        """

        assert field in self.data_keys(), 'Requested field not found.'


    def add_metadata(self, subject, experiment, session):
        """Add metadata information to task object.

        Parameters
        ----------
        subject : str
            Subject label.
        experiment : str
            Name of the experiment.
        session : str
            Session label.
        """

        self.meta['subject'] = subject
        self.meta['experiment'] = experiment
        self.meta['session'] = session


    def set_status(self, label, status):
        """Set a status marker.

        Parameters
        ----------
        label : str
            The label of which status marker to update.
        status : bool
            The status to update to.
        """

        assert label in self.status.keys(), 'Status label not understood.'
        self.status[label] = status


    def set_info(self, label, info):
        """Set an info marker.

        Parameters
        ----------
        label : str
            The label of which status marker to update.
        info
            The info to update.
        """

        assert label in self.info.keys(), 'Info label not understood.'
        self.info[label] = info


    def copy(self):
        """Return a deepcopy of this object."""

        return deepcopy(self)


    def data_keys(self, skip=None):
        """Get a list of data keys defined in the task object.

        Parameters
        ----------
        skip : str or list of str
            Name(s) of any data attributes to skip.

        Returns
        -------
        data_keys : list of str
            List of data attributes available in the object.
        """

        data_keys = list(vars(self).keys())

        # Drop the 'status' attribute, which doesn't store data
        data_keys.remove('status')

        if skip:
            for skip_item in [skip] if isinstance(skip, str) else skip:
                data_keys.remove(skip_item)

        return data_keys


    def drop_fields(self, fields):
        """Drop field(s) from the task object.

        Parameters
        ----------
        fields : str or list of str
            Field(s) to drop.
        """

        fields = [fields] if isinstance(fields, str) else fields
        for field in fields:
            self._check_field(field)
            delattr(self, field)


    def drop_keys(self, field, keys):
        """Drop key(s) from a specified field of the task object.

        Parameters
        ----------
        field : str
            Which field to access and remove keys from.
        keys : list of str or dict
            Which key(s) of the field to remove.
        """

        self._check_field(field)
        keys = [keys] if isinstance(keys, str) else keys

        data = getattr(self, field)
        for key in keys:
            data.pop(key)


    def apply_func(self, field, keys, func, **kwargs):
        """Apply a given function across a set of specified fields.

        Parameters
        ----------
        field : str
            Which field to access data to apply function to.
        keys : list of str or dict
            Which key(s) of the field to apply function to.
            If list, should be a list of keys available in `field`.
            If dict, keys should be subfields, each with corresponding labels to typecast.
        func : callable
            Function to apply to the selected fields.
        **kwargs
            Keyword arguments to pass into `func`.
        """

        self._check_field(field)
        data = getattr(self, field)
        for key in [keys] if isinstance(keys, (str, dict)) else keys:
            if isinstance(key, str):
                data[key] = func(data[key], **kwargs)
            else:
                for okey, ikeys in key.items():
                    for ikey in [ikeys] if isinstance(ikeys, str) else ikeys:
                        data[okey][ikey] = func(data[okey][ikey], **kwargs)


    def convert_type(self, field, keys, dtype):
        """Convert the type of specified data fields.

        Parameters
        ----------
        field : str
            Which field to access data to convert type.
        keys : list of str or dict
            Which key(s) of the field to convert type.
            If list, should be a list of keys available in `field`.
            If dict, keys should be subfields, each with corresponding labels to typecast.
        dtype : type
            The data type to cast the variables to.
        """

        self.apply_func(field, keys, convert_type, dtype=dtype)


    def convert_to_array(self, field, keys, dtype):
        """Convert specified data fields to numpy arrays.

        Parameters
        ----------
        field : str
            Which field to access data to convert to array.
        keys : list of str or dict
            Which key(s) of the field to convert to array.
            If list, should be a list of keys available in `field`.
            If dict, keys should be subfields, each with corresponding labels to typecast.
        dtype : type
            The data type to give the converted array.
        """

        self.apply_func(field, keys, convert_to_array, dtype=dtype)


    def get_trial(self, index, field=None):
        """Get the information for a specified trial.

        Parameters
        ----------
        index : int
            The index of the trial to access.
        field : str, optional, default: None
            Which trial data to access.
        """

        trial_data = getattr(self, 'trial')
        if field:
            trial_data = trial_data[field]

        trial_info = dict()
        for key in trial_data.keys():
            # Collect trial info, skipping dictionaries, which are subevents
            if not isinstance(trial_data[key], dict):
                trial_info[key] = trial_data[key][index]

        return trial_info


    def plot_sync_allignment(self, n_pulses=None):
        """Plot alignment of the synchronization pulses.

        Parameters
        ----------
        n_pulses : int, optional
            Number of pulses to plot.
        """

        # should be implemented in subclass
        raise NotImplementedError


    def update_time(self, update, skip=None, apply_type=None, **kwargs):
        """Offset all timestamps within the task object.

        Parameters
        ----------
        update : {'offset', 'change_units', 'predict_times'} or callable
            What kind of update to do to the timestamps.
        skip : str, optional
            Fields set to skip.
        apply_type : type, optional
            If given, only apply update to specific type.
        kwargs
            Additional arguments to pass to the update function.
        skip : str or list of str, optional
            Any data fields to skip during the updating.
        """

        # Select update function to use
        if isinstance(update, str):
            available = ['offset', 'change_units', 'predict_times']
            assert update in available, \
                "Update approach doesn't match whats available: ".format(available)
            func = TIME_UPDATES[update]
        else:
            func = update

        # Update any fields with 'time' in their name
        #   Note: this update goes down up to two levels of embedded dictionaries
        for field in self.data_keys(skip):
            data = getattr(self, field)
            for key in data.keys():
                if isinstance(data[key], dict):
                    for subkey in data[key].keys():
                        if 'time' in subkey and not is_empty(data[key][subkey]) \
                            and is_type(data[key][subkey], apply_type):
                            data[key][subkey] = func(data[key][subkey], **kwargs)
                else:
                    if 'time' in key and not is_empty(data[key]) and is_type(data[key], apply_type):
                        data[key] = func(data[key], **kwargs)

        # Update status information about the reset
        if update == 'offset':
            self.set_status('time_reset', True)
            self.set_info('time_offset', kwargs['offset'])
        if update == 'predict_times':
            self.set_status('time_aligned', True)


    def to_dict(self):
        """Convert object data to a dictionary."""

        out_dict = {}
        for key in self.data_keys():
            out_dict[key] = getattr(self, key)

        return out_dict


    @check_dependency(pd, 'pandas')
    def to_dataframe(self, field):
        """Return a specified field as a dataframe.

        Parameters
        ----------
        field : str
            Which field to access to return as a dataframe.

        Returns
        -------
        pd.DataFrame
            Dataframe representation of the requested field.
        """

        self._check_field(field)
        return pd.DataFrame(getattr(self, field))
