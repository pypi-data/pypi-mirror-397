import mne
import numpy as np
from pathlib import Path


def load_edf(path: str):
    """
    Load an EDF EEG file and return raw signal + raw metadata.

    Parameters
    ----------
    path : str
        Path to EDF file

    Returns
    -------
    signal : np.ndarray
        Raw signal array with shape [channels, time]
    metadata : dict
        Raw metadata extracted from the file
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"EDF file not found: {path}")

    # Read EDF using MNE
    raw = mne.io.read_raw_edf(path, preload=True, verbose=False)

    # Extract raw signal
    signal = raw.get_data()  # shape: [channels, time]

    # Extract metadata (NO cleaning / NO inference)
    metadata = {
        "sfreq": raw.info.get("sfreq"),
        "ch_names": raw.info.get("ch_names"),
        "nchan": raw.info.get("nchan"),
        "duration_sec": raw.n_times / raw.info.get("sfreq"),
        "raw_info": raw.info,  # full MNE info object
    }

    return signal, metadata