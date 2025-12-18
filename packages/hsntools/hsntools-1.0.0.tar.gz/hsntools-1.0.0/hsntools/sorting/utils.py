"""Utilities related to spike sorting / combinato files."""

import numpy as np

###################################################################################################
###################################################################################################

def get_sorting_kept_labels(groups):
    """Get the valid clas / group information from the combinato organized groups info array.

    Parameters
    ----------
    group : 2d array
        Combinato organized array of class and group information.
        1st column: class index / label; 2nd column: group assignment.

    Returns
    -------
    valid_classes : 1d array
        An array of the class assignments that reflect valid (to-be-kept) spikes.
    valid_groups : 1d array
        An array of the group assignments that reflect valid (to-be-kept) spikes.

    Notes
    -----
    In Combinato, there are two special cases of groups we want to avoid:
    - '0': contains unassigned events (failed to be put in a class during clustering)
    - '-1': classes that are assigned to the artifacts group

    To get information about class labels that contain valid spikes (that we want to
    keep / extract), this function excludes 0 and -1 group labels.
    """

    # Separate columns: class indices and group assignments
    class_labels, group_labels = groups.T

    # Create a mask for all valid cluster label: excludes 0 (unassigned) and -1 (artifacts)
    mask = group_labels > 0

    # Get the set of valid clusters & groups
    valid_classes = class_labels[mask]
    valid_groups = group_labels[mask]

    return valid_classes, valid_groups


def get_group_labels(class_labels, groups):
    """Get the group label for each spike (based on spike class + group mapping).

    Parameters
    ----------
    class_labels : 1d array
        Class assignment of each spike, as extracted from the sorting data.
    groups : 2d array
        Class and group assignment mapping, as extracted from the sorting data.

    Returns
    -------
    group_labels : 1d array
        Group label for each spike.
    """

    group_labels = np.zeros(len(class_labels), dtype=int)
    for ind, cval in enumerate(class_labels):
        group_labels[ind] = groups[:, 1][cval == groups[:, 0]]

    return group_labels


def extract_clusters(data):
    """Extract individual clusters from a channel of data.

    Parameters
    ----------
    data : dict
        Spike sorting information from a channel of data.
        Should include the keys: `times`, `waveforms`, `clusters`, `classes`.

    Returns
    -------
    cluster_times : list of 1d array
        Spike times, separated for each cluster. List has length of n_clusters.
    cluster_waveforms : list of 2d array
        Spike waveforms, separated for each cluster. List has length of n_clusters.
    """

    clusters = []
    for cluster_ind in set(data['clusters']):
        mask = data['clusters'] == cluster_ind

        cluster_info = {}
        cluster_info['ind'] = cluster_ind
        cluster_info['channel'] = data['channel']
        cluster_info['polarity'] = data['polarity']
        cluster_info['times'] = data['times'][mask]
        cluster_info['waveforms'] = data['waveforms'][mask, :]
        cluster_info['classes'] = data['classes'][mask]
        clusters.append(cluster_info)

    return clusters
