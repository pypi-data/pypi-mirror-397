from typing import Tuple, List
import numpy as np
from scipy.signal import resample_poly
import math


def normalize_time(
    signal: np.ndarray,
    original_fs: float,
    target_fs: float = 256.0,
) -> Tuple[np.ndarray, float, List[str]]:
    """
    Normalize EEG signal to a target sampling rate.

    Rules:
    - If original_fs == target_fs -> no-op
    - If original_fs < target_fs -> upsample (warn)
    - If original_fs > target_fs -> downsample (safe)
    """

    warnings = []

    if original_fs is None:
        raise ValueError("Original sampling rate is missing")

    if target_fs is None:
        return signal, original_fs, warnings

    if math.isclose(original_fs, target_fs):
        return signal, original_fs, warnings

    if original_fs < target_fs:
        warnings.append(
            f"Upsampling from {original_fs} Hz to {target_fs} Hz"
        )
    else:
        warnings.append(
            f"Downsampling from {original_fs} Hz to {target_fs} Hz"
        )

    # Compute rational resampling factors
    up = int(target_fs)
    down = int(original_fs)

    # Polyphase resampling (stable, deterministic)
    resampled = resample_poly(signal, up=up, down=down, axis=1)

    return resampled, target_fs, warnings