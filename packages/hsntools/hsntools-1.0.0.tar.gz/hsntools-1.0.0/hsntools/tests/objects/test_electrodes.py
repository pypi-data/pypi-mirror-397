"""Tests for hsntools.objects.electrodes"""

import os

import pandas as pd

from hsntools.tests.tsettings import TEST_FILE_PATH

from hsntools.objects.electrodes import *

###################################################################################################
###################################################################################################

def test_bundle():

    bundle = Bundle('probe', 'hemisphere', 'lobe', 'region')
    assert bundle

    bdict = bundle.to_dict()
    assert isinstance(bdict, dict)

def test_electrodes():

    electrodes = Electrodes('subject', 30000)
    assert electrodes

def test_electrodes_add_bundle():

    electrodes = Electrodes('subject', 30000)
    electrodes.add_bundle('probe', 'hemisphere', 'lobe', 'region')
    assert electrodes.n_bundles
    assert electrodes.bundles

def test_electrodes_add_bundle_bundle(tbundle):

    electrodes = Electrodes('subject', 30000)
    electrodes.add_bundle(tbundle)
    assert electrodes.bundles[0] == tbundle

def test_electrodes_add_bundles():

    bundles = [
        {'probe' : 'tname1', 'hemisphere' : 'themi1', 'lobe' : 'tlobe1', 'region' : 'tregion1'},
        {'probe' : 'tname2', 'hemisphere' : 'themi2', 'lobe' : 'tlobe2', 'region' : 'tregion2'},
    ]

    electrodes = Electrodes('subject', 30000)
    electrodes.add_bundles(bundles)
    assert electrodes.bundles
    assert electrodes.n_bundles == len(bundles)

    # check bundles using iteration across object
    for ind, bundle in enumerate(electrodes):
        for bkey in electrodes.bundle_properties:
            if bkey in bundles[0].keys():
                assert getattr(electrodes.bundles[ind], bkey) == bundles[ind][bkey]
            else:
                assert getattr(electrodes.bundles[ind], bkey) is None

def test_electrodes_add_bundles_bundle(tbundle):

    electrodes = Electrodes('subject', 30000)
    bundles = [tbundle, tbundle]
    electrodes.add_bundles(bundles)
    assert electrodes.bundles
    assert electrodes.n_bundles == len(bundles)

def test_electrodes_get(telectrodes):

    probes = telectrodes.get('probe')
    assert probes == ['tname1', 'tname2']

    regions = telectrodes.get('region')
    assert regions == ['tregion1', 'tregion2']

def test_electrodes_to_dict(telectrodes):

    odict = telectrodes.to_dict(drop_empty=False)
    assert isinstance(odict, dict)

    blabels = telectrodes.bundle_properties
    blabels.remove('channels')
    for bkey in blabels:
        assert len(odict[bkey]) == telectrodes.n_bundles * telectrodes.n_electrodes_per_bundle
    for ind, bundle in enumerate(telectrodes):
        for bkey in blabels:
            assert odict[bkey][ind * 8] == getattr(telectrodes.bundles[ind], bkey)

def test_electrodes_to_dataframe(telectrodes):

    df = telectrodes.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == telectrodes.n_bundles * telectrodes.n_electrodes_per_bundle

def test_electrodes_to_csv(telectrodes):

    test_fname = 'test_electrodes_csv'
    telectrodes.to_csv(test_fname, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH / (test_fname + '.csv'))
