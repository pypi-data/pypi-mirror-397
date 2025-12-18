from typing import List, Tuple
import numpy as np

# Minimal, ML-safe canonical 10–20 set
CANONICAL_10_20 = [
    "FP1", "FP2",
    "F3", "F4",
    "C3", "C4",
    "P3", "P4",
    "O1", "O2",
    "FZ", "CZ", "PZ",
]


def map_to_10_20(
    signal: np.ndarray,
    channel_names: List[str],
) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Project EEG to a canonical 10–20 channel set.

    Returns
    -------
    mapped_signal : np.ndarray
        Signal with only canonical channels, ordered.
    mapped_channels : list[str]
        Ordered canonical channel names present in data.
    warnings : list[str]
        Human-readable warnings about drops / missing channels.
    """
    warnings = []

    # Build index map: channel name -> index
    name_to_idx = {name: i for i, name in enumerate(channel_names)}

    present = []
    indices = []

    for ch in CANONICAL_10_20:
        if ch in name_to_idx:
            present.append(ch)
            indices.append(name_to_idx[ch])

    # Warnings
    dropped = [ch for ch in channel_names if ch not in CANONICAL_10_20]
    missing = [ch for ch in CANONICAL_10_20 if ch not in present]

    if dropped:
        warnings.append(f"Dropped non-10–20 channels: {', '.join(dropped)}")

    if missing:
        warnings.append(f"Missing canonical channels: {', '.join(missing)}")

    if not indices:
        raise ValueError("No canonical 10–20 channels found in EEG data")

    mapped_signal = signal[indices, :]

    return mapped_signal, present, warnings