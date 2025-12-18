"""Defines defaults for a single-unit project layout."""

###################################################################################################
###################################################################################################

PROJECT_FOLDERS = [
    'docs',
    'info',
    'nwb',
    'recordings',
]

SUBJECT_FOLDERS = [
    'anatomy',
    'electrodes',
    'notes',
]

SESSION_FOLDERS = {
    '01_raw' : [
        'behavior',
        'neural',
    ],
    '02_processing' : [
        'alignment',
        'metadata',
        'sorting',
        'task',
    ],
    '03_extracted' : [
        'spikes',
        'lfp',
    ],
}
