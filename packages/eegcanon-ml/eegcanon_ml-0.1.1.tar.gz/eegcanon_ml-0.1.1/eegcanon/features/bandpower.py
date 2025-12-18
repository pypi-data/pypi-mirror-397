import numpy as np
from scipy.signal import welch


BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
}


def bandpower(epoch, fs):
    powers = []

    for ch in epoch:
        freqs, pxx = welch(ch, fs=fs, nperseg=fs * 2)
        band_feats = []

        for low, high in BANDS.values():
            idx = (freqs >= low) & (freqs <= high)
            band_feats.append(np.sum(pxx[idx]))

        powers.append(band_feats)

    return np.array(powers)  # (channels, bands)