"""Functions for aligning timestamps."""

import numpy as np

from hsntools.modutils.dependencies import safe_import, check_dependency

sklearn = safe_import('sklearn')
stats = safe_import('.stats', 'scipy')

###################################################################################################
###################################################################################################

@check_dependency(sklearn, 'sklearn')
def fit_sync_alignment(sync_behav, sync_neural, score_thresh=0.9999,
                       ignore_poor_alignment=False, return_model=False, verbose=False):
    """Fit a model to align synchronization pulses from different recording systems.

    Parameters
    ----------
    sync_behav : 1d array
        Sync pulse times from behavioral computer.
    sync_neural : 1d array
        Sync pulse times from neural computer.
    score_thresh : float, optional, default: 0.9999
        R^2 threshold value to check that the fit model is better than.
    ignore_poor_alignment : bool, optional, default: False
        Whether to ignore a bad alignment score.
    return_model : bool, optional, default: False
        Whether to return the model object. If False, returns
    verbose : bool, optional, default: False
        Whether to print out model information.

    Returns
    -------
    model : LinearRegression
        The fit model object. Only returned if `return_model` is True.
    model_intercept : float
        Intercept of the model predicting differences between sync pulses.
        Returned if `return_model` is False.
    model_coef : float
        Learned coefficient of the model predicting  differences between sync pulses.
        Returned if `return_model` is False.
    score : float
        R^2 score of the model, indicating how good a fit there is between sync pulses.
    """

    # sklearn imports are weird, so re-import here
    #   the sub-modules here aren't available from the global namespace
    from sklearn.metrics import r2_score
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    # Reshape to column arrays for scikit-learn
    sync_behav = sync_behav.reshape(-1, 1)
    sync_neural = sync_neural.reshape(-1, 1)

    # Linear model to predict alignment between time traces
    x_train, x_test, y_train, y_test = train_test_split(\
        sync_behav, sync_neural, test_size=0.50, random_state=42)

    model = LinearRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    score = r2_score(y_test, y_pred)
    bad_score_msg = 'This session has bad synchronization alignment.'
    if score < score_thresh:
        if not ignore_poor_alignment:
            raise ValueError(bad_score_msg)
        else:
            print(bad_score_msg)

    if verbose:
        print('coef', model.coef_[0], '\n intercept', model.intercept_[0])
        print('score', score)

    if return_model:
        return model, score
    else:
        return model.intercept_[0], model.coef_[0][0], score


def predict_times(times, intercept, coef):
    """Predict times alignment from model coefficients.

    Parameters
    ----------
    times : 1d array
        Timestamps to align.
    intercept : float
        Learned intercept of the model predicting differences between sync pulses.
    coef : float
        Learned coefficient of the model predicting differences between sync pulses.

    Returns
    -------
    1d array
        Predicted times, after applying time alignment.
    """

    return coef * np.array(times).astype(float) + intercept


def predict_times_model(times, model):
    """Predict times alignment from a model object.

    Parameters
    ----------
    times : 1d array
        Timestamps to align.
    model : LinearRegression
        A model object, with a fit model predicting timestamp alignment.

    Returns
    -------
    1d array
        Predicted times, after applying time alignment.
    """

    return model.predict(times.reshape(-1, 1))


@check_dependency(stats, 'scipy')
def match_pulses(sync_behav, sync_neural, n_pulses, start_offset=None):
    """Match pulses to each other based on ISIs.

    Parameters
    ----------
    sync_behav, sync_neural : 1d array
        Synchronization pulses from the behavioral and neural computers.
    n_pulses : int
        The number of pulses to match by.
    start_offset : int, optional
        Number of pulses to shift away from the start of the task recording.

    Returns
    -------
    sync_behav_out, sync_neural_out : 1d array
        Matched synchronization pulses from the behavioral and neural computers.

    Notes
    -----
    Using a `start_offset` can be useful if there are bad synchronization
    results due to recording pause at the start.
    """

    from scipy import __version__ as scipy_version

    isi_sb = np.diff(sync_behav)
    isi_sn = np.diff(sync_neural)

    ixis = []
    # Iterate through neural sync pulses, and collect index offsets for matching ISIs
    for ixn, isi in enumerate(isi_sn):

        # Find matching ISI, and get first match in behavioral
        if isi in isi_sb:
            ixb = np.where(isi_sb == isi)
            ixb = ixb[0][0]

            # Break if end of ISI list reached
            if ixb + 1 >= len(isi_sb) or ixn + 1 >= len(isi_sn):
                break

            # Check if next ISI matches - if so, record the index difference
            elif isi_sn[ixn + 1] == isi_sb[ixb + 1]:
                ixis += [ixb - ixn]

    # Find mode of index offsets - with a special check for scipy version
    version_vals = scipy_version.split('.')
    # Old version - prior to `keep_dims` being added in 1.9
    if int(version_vals[0]) == 1 and int(version_vals[1]) < 9:
        ixis_mode = stats.mode(ixis)[0][0]
    else:
        ixis_mode = stats.mode(ixis, keepdims=True).mode[0]

    # Select sync vectors
    if start_offset is not None:
        # Choose sync vector starting at chosen index rather than the beginning
        sync_behav_out = sync_behav[ixis_mode + start_offset : ixis_mode + start_offset + n_pulses]
        sync_neural_out = sync_neural[start_offset : start_offset + n_pulses]
    else:
        # Otherwise, sync vector from beginning with offset accounted for
        sync_behav_out = sync_behav[ixis_mode : ixis_mode + n_pulses]
        sync_neural_out = sync_neural[0 : n_pulses]

    return sync_behav_out, sync_neural_out
