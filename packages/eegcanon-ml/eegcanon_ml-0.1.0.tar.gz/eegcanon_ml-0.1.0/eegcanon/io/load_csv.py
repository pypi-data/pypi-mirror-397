import pandas as pd
import numpy as np
from pathlib import Path


def load_csv(path: Path):
    """
    Load EEG data from a CSV file.

    Expected format:
    - First column: time (seconds)
    - Remaining columns: EEG channels
    """

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)

    if df.shape[1] < 2:
        raise ValueError("CSV must contain time column + at least one channel")

    # First column must be time
    time_col = df.columns[0]
    time = df[time_col].values

    # Compute sampling rate
    if len(time) < 2:
        raise ValueError("Not enough samples to infer sampling rate")

    dt = np.mean(np.diff(time))
    sfreq = round(1.0 / dt, 3)

    # Channel data
    ch_names = list(df.columns[1:])
    signal = df[ch_names].to_numpy().T  # (channels, time)

    metadata = {
        "ch_names": ch_names,
        "sfreq": sfreq,
        "source_format": "CSV",
        "time_column": time_col,
    }

    return signal, metadata