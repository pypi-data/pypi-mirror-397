"""Processing functions related to spike sorting / combinato files."""

import numpy as np

from hsntools.io.sorting import load_combinato_spike_file, load_combinato_sorting_file, save_units
from hsntools.sorting.utils import get_sorting_kept_labels, get_group_labels, extract_clusters

###################################################################################################
###################################################################################################

def collect_all_sorting(spike_data, sort_data):
    """Collect together all the organized spike sorting information for a channel of data.

    Parameters
    ----------
    spike_data : dict
        Loaded data from the spike data file.
        Should include the keys: `times`, `waveforms`.
    sort_data : dict
        Loaded sorting data from the spike sorting data file.
        Should include the keys: `index`, `classes`, `groups`.

    Returns
    -------
    outputs : dict
        Each value is an array of all values for valid events in the channel of data, including:

        * `times` : spike times for each event
        * `waveforms` : spike waveform for each event
        * `classes` : class assignment for each event
        * `clusters` : cluster (group) assignment for each event

    Notes
    -----
    Kept information is for all valid spikes - all clusters considered putative single units.

    This excludes:

    - spike events detected but excluded from sorting due to being listed as artifact
    - spike events entered into sorting, but that are unassigned to a group
    - spike events sorted into a group, but who's group was listed as an artifact
    """

    assert spike_data['channel'] == sort_data['channel'], "Data file channels do not match."
    assert spike_data['polarity'] == sort_data['polarity'], "Data file polarity does not match."

    # Get the set of valid class & group labels, and make a mask
    valid_classes, valid_groups = get_sorting_kept_labels(sort_data['groups'])
    class_mask = np.isin(sort_data['classes'], valid_classes)

    # Create a vector reflecting group assignment of each spike
    group_labels = get_group_labels(sort_data['classes'], sort_data['groups'])

    outputs = {

        # collect metadata into output
        'channel' : spike_data['channel'],
        'polarity' : spike_data['polarity'],

        # spike data collected as the non-artifact spikes, sub-selected for valid classes
        'times' : spike_data['times'][sort_data['index']][class_mask],
        'waveforms' : spike_data['waveforms'][sort_data['index'][class_mask], :],

        # spike sorting information collected as the valid class labels
        'classes' : sort_data['classes'][class_mask],
        'clusters' : group_labels[class_mask],
    }

    return outputs


def process_combinato_data(channel, input_folder, polarity, user, units_folder,
                           continue_on_fail=False, verbose=True):
    """Helper function to run the process of going from combinato -> extracted units files.

    Parameters
    ----------
    channel : int or str
        The channel number / label of the file to load.
    input_folder : str or Path
        The folder location to load the spike data from.
    polarity : {'neg', 'pos'}
        Which polarity of detected spikes to load.
    user : str
        The 3 character user label to load.
    output_folder : str or Path
        The folder destination to save the output units files to.
    continue_on_fail : bool, optional, default: False
        Whether to continue when an error is encountered.
    verbose : bool, optional, default: True
        Whether to print out updates about the extraction.
    """

    try:

        # Load spike & sorting data
        spike_data = load_combinato_spike_file(channel, input_folder, polarity)
        sort_data = load_combinato_sorting_file(channel, input_folder, polarity, user)

        # Organize and collect extracted data together, and extract unit clusters
        clusters = collect_all_sorting(spike_data, sort_data)
        units = extract_clusters(clusters)

        # Save out extracted unit data
        save_units(units, units_folder)

        if verbose:
            print('Extracted channel {:20s} - found {:2d} clusters\t\t'.format(\
                channel, len(units)))

    except:
        if not continue_on_fail:
            raise
        if verbose:
            print('Issue extracting channel: {}'.format(channel))
