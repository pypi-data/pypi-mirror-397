"""Neural Signal Processor (NSP) related I/O functions.

Functionality in this file requires the `neo` module: https://github.com/NeuralEnsemble/python-neo
"""

from hsntools.io.utils import check_folder
from hsntools.modutils.dependencies import safe_import, check_dependency
from hsntools.timestamps.utils import compute_sample_length

neo = safe_import('neo')

###################################################################################################
###################################################################################################

@check_dependency(neo, 'neo')
def load_blackrock(file_name, folder, nsx_to_load=None, load_nev=None):
    """Load a set of Blackrock files.

    Parameters
    ----------
    file_name : str
        The file name to load.
    folder : str or Path
        The folder to load the file(s) from.
    nsx_to_load : int or list, optional
        Which nsx file(s) to load.
    load_nev : bool, optional, default: True
        Whether to load the nev file.

    Returns
    -------
    reader : neo.rawio.blackrockrawio.BlackrockRawIO
        Blackrock file reader.
    """

    reader = neo.rawio.BlackrockRawIO(\
        check_folder(file_name, folder), nsx_to_load=nsx_to_load, load_nev=load_nev)
    reader.parse_header()

    return reader


def check_blackrock_file_info(reader):
    """Check some basic information and metadata from a set of Blackrock files.

    Parameters
    ----------
    reader : neo.rawio.blackrockrawio.BlackrockRawIO
        File reader for the Blackrock file(s).
    """

    str_fmt = '  seg#{}    start: {:1.2e}    stop: {:1.2e}    size: {:10d}    tlen: {:4.2f}'

    fs = reader.get_signal_sampling_rate()
    n_chans = reader.signal_channels_count(0)

    print('sampling rate: \t', fs)
    print('# channels: \t', n_chans)

    n_blocks = reader.block_count()
    for bi in range(n_blocks):
        print('block #{}:'.format(bi))
        n_segments = reader.segment_count(bi)
        for si in range(n_segments):
            seg_start = reader.segment_t_start(bi, si)
            seg_stop = reader.segment_t_stop(bi, si)
            seg_size = reader.get_signal_size(bi, si)
            seg_length = compute_sample_length(seg_size, fs)
            print(str_fmt.format(si, seg_start, seg_stop, seg_size, seg_length))
