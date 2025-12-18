"""Base electrodes class."""

from copy import deepcopy

from hsntools.io.utils import check_ext, check_folder
from hsntools.modutils.dependencies import safe_import, check_dependency

pd = safe_import('pandas')

###################################################################################################
###################################################################################################

class Bundle():
    """Object for collecting & managing an electrode bundle definition."""

    def __init__(self, probe, hemisphere=None, lobe=None, region=None,
                 subregion=None, channels=None):
        """Initialize Bundle object."""

        self.probe = probe
        self.hemisphere = hemisphere
        self.lobe = lobe
        self.region = region
        self.subregion = subregion
        self.channels = channels

    def to_dict(self):
        """Export object information to a dictionary"""

        return {
            'probe' : self.probe,
            'hemisphere' : self.hemisphere,
            'lobe' : self.lobe,
            'region' : self.region,
            'subregion' : self.subregion,
            'channels' : self.channels,
        }


class Electrodes():
    """Object for collecting & managing electrode information.

    Attributes
    ----------
    subject : str
        Subject label.
    fs : int
        Sampling rate.
    bundles : list of Bundle
        Names of the bundles.
    """

    n_electrodes_per_bundle = 8

    def __init__(self, subject=None, fs=None):
        """Initialize Electrodes object."""

        self.subject = subject
        self.fs = fs
        self.bundles = []


    def __iter__(self):
        """Iterate across bundles in the object."""

        for ind in range(self.n_bundles):
            yield self.bundles[ind]


    @property
    def n_bundles(self):
        """The number of bundles stored in the object."""

        return len(self.bundles)


    @property
    def bundle_properties(self):
        """Access bundle property labels."""

        if self.bundles:
            bundle_properties = list(self.bundles[0].to_dict().keys())
        else:
            bundle_properties = []

        return bundle_properties


    def add_bundle(self, probe, hemisphere=None, lobe=None, region=None,
                   subregion=None, channels=None):
        """Add a bundle to the object.

        Parameters
        ----------
        probe : Bundle or str
            Name of the bundle, if string, or pre-initialized Bundle object.
        hemisphere : {'left', 'right'}, optional
            The hemisphere the probe is implanted in.
        lobe : {'frontal', 'parietal', 'temporal', 'occipital'}, optional
            Which lobe the probe is in.
        region : str, optional
            Location of the bundle.
        subregion : str, optional
            The subregion specifier of the probe.
        channels : list of int, optional
            A set of channel indices for the bundle.
        """

        if isinstance(probe, Bundle):
            self.bundles.append(probe)
        else:
            self.bundles.append(Bundle(probe, hemisphere, lobe, region, subregion, channels))


    def add_bundles(self, bundles):
        """Add multiple bundles to the object.

        Parameters
        ----------
        names : Bundle or list of dict
            Names of the bundles.
        """

        for bundle in bundles:
            if isinstance(bundle, Bundle):
                self.add_bundle(bundle)
            else:
                self.add_bundle(**bundle)


    def get(self, field):
        """Get the values for a specified field from across all bundles.

        Parameters
        ----------
        field : {'probe', 'hemisphere', 'lobe', 'region', 'subregion', 'channels'}
            Which field to get the values for.

        Returns
        -------
        list
            Values for the specified field from across all defined bundles.
        """

        return [getattr(bundle, field) for bundle in self.bundles]


    def copy(self):
        """Return a deepcopy of this object."""

        return deepcopy(self)


    def to_dict(self, drop_empty=True):
        """Convert object data to a dictionary.

        Parameters
        ----------
        drop_empty : bool, optional, default: True
            Whether to drops fields that are all None.
        """

        labels = self.bundle_properties
        labels.remove('channels')

        out_dict = {label : [] for label in labels}
        for label in ['label', 'pin', 'channel']:
            out_dict[label] = []

        for bundle in self.bundles:
            for ind in range(self.n_electrodes_per_bundle):
                out_dict['label'].append(bundle.probe + str(ind + 1))
                out_dict['pin'].append(ind + 1)
                for label in labels:
                    out_dict[label].append(getattr(bundle, label))
                if bundle.channels is not None:
                    out_dict['channel'].append(bundle.channels[ind])
                else:
                    out_dict['channel'].append(None)

        # Drop any entries in the dictionary conversion that are empty or all None
        if drop_empty:
            for dlabel in list(out_dict.keys()):
                if set(out_dict[dlabel]) == {None}:
                    out_dict.pop(dlabel)

        return out_dict


    @check_dependency(pd, 'pandas')
    def to_dataframe(self):
        """Return object data as a dataframe."""

        return pd.DataFrame(self.to_dict())


    @check_dependency(pd, 'pandas')
    def to_csv(self, file_name, folder=None, **kwargs):
        """Save out the electrode information as a CSV file.

        Parameters
        ----------
        file_name : str
            The file name to save.
        folder : str
            The folder to save the file to.
        **kwargs
            Additional keyword arguments to pass to pd.DataFrame.to_csv().
        """

        self.to_dataframe().to_csv(check_ext(check_folder(file_name, folder), '.csv'), **kwargs)
