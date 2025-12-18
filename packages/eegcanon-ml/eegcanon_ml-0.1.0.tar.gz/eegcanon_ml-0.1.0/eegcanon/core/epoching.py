import numpy as np


def epoch_signal(
    signal: np.ndarray,
    sampling_rate: float,
    window: float,
    overlap: float,
    drop_last: bool = True,
):
    """
    Convert continuous EEG into epochs.

    Parameters
    ----------
    signal : np.ndarray
        Shape (channels, time)
    sampling_rate : float
        Sampling frequency in Hz
    window : float
        Window length in seconds
    overlap : float
        Overlap between windows in seconds
    """

    if overlap >= window:
        raise ValueError("overlap must be smaller than window")

    win_samples = int(window * sampling_rate)
    step_samples = int((window - overlap) * sampling_rate)

    if win_samples <= 0 or step_samples <= 0:
        raise ValueError("Invalid window or overlap")

    epochs = []

    for start in range(0, signal.shape[1] - win_samples + 1, step_samples):
        end = start + win_samples
        epochs.append(signal[:, start:end])

    epochs = np.stack(epochs, axis=0)

    return epochs