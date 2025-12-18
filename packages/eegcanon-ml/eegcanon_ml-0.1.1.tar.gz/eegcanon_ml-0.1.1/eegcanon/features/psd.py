import numpy as np
from scipy.signal import welch


def compute_psd(epoch, fs):
    """
    Compute mean PSD per channel
    """
    psd_vals = []
    for ch in epoch:
        freqs, pxx = welch(ch, fs=fs, nperseg=fs * 2)
        psd_vals.append(np.mean(pxx))
    return np.array(psd_vals)