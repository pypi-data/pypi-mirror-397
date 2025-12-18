from typing import Tuple, List


def check_sampling_rate(sfreq: float) -> Tuple[float, List[str]]:
    """
    Validate EEG sampling rate and return warnings if needed.
    """
    warnings = []

    if sfreq is None:
        raise ValueError("Sampling rate is missing")

    if sfreq < 100:
        warnings.append(
            f"Sampling rate {sfreq} Hz is low; may miss higher-frequency activity"
        )

    if sfreq > 1000:
        warnings.append(
            f"Sampling rate {sfreq} Hz is unusually high; consider downsampling"
        )

    return sfreq, warnings