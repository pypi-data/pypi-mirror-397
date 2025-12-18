from datetime import datetime
from typing import List

from eegcanon.io.load_file import load_file

from eegcanon.infer.channels import normalize_channel_names
from eegcanon.infer.montage import map_to_10_20
from eegcanon.infer.sampling import check_sampling_rate

from eegcanon.normalize.time import normalize_time

from eegcanon.core.canonical import CanonicalEEG
from eegcanon.core.warnings import EEGWarning
from eegcanon.core.policy import ChannelPolicy, TEN_TWENTY_MINIMAL


def load_eeg(
    path: str,
    channel_policy: ChannelPolicy = TEN_TWENTY_MINIMAL,
    target_fs: float = 256.0,
) -> CanonicalEEG:
    """
    Load an EEG file and return a CanonicalEEG object.

    This function enforces:
    - format abstraction
    - channel name normalization
    - 10–20 spatial standardization
    - sampling-rate sanity checks
    - time normalization (resampling)
    - structured warnings
    - full provenance tracking
    """

    warnings: List[EEGWarning] = []

    # -------------------------------------------------
    # 1. IO Layer
    # -------------------------------------------------
    signal, metadata = load_file(path)

    # -------------------------------------------------
    # 2. Channel Name Cleanup
    # -------------------------------------------------
    clean_names = normalize_channel_names(metadata["ch_names"])

    # -------------------------------------------------
    # 3. Channel Policy (10–20 Mapping)
    # -------------------------------------------------
    mapped_signal, mapped_channels, ch_warnings = map_to_10_20(
        signal, clean_names
    )

    if ch_warnings:
        warnings.append(
            EEGWarning(
                type="CHANNEL_DROP",
                severity="INFO",
                message="Non-canonical channels were dropped",
                affected=ch_warnings,
            )
        )

    # -------------------------------------------------
    # 4. Sampling Rate Sanity
    # -------------------------------------------------
    sfreq, fs_warnings = check_sampling_rate(metadata["sfreq"])

    for w in fs_warnings:
        warnings.append(
            EEGWarning(
                type="FS_SANITY",
                severity="WARN",
                message=w,
            )
        )

    # -------------------------------------------------
    # 5. Time Normalization (Resampling)
    # -------------------------------------------------
    norm_signal, norm_fs, time_warnings = normalize_time(
        mapped_signal,
        original_fs=sfreq,
        target_fs=target_fs,
    )

    for w in time_warnings:
        warnings.append(
            EEGWarning(
                type="TIME_NORMALIZATION",
                severity="WARN",
                message=w,
            )
        )

    # -------------------------------------------------
    # 6. Provenance (Audit Trail)
    # -------------------------------------------------
    provenance = {
        "source_format": metadata.get("source_format", "EDF"),
        "channel_policy": channel_policy.name,
        "original_fs": sfreq,
        "target_fs": norm_fs,
        "time_normalized": sfreq != norm_fs,
        "load_time": datetime.utcnow().isoformat(),
    }

    # -------------------------------------------------
    # 7. Canonical EEG Object
    # -------------------------------------------------
    return CanonicalEEG(
        data=norm_signal,
        channels=mapped_channels,
        sampling_rate=norm_fs,
        policy=channel_policy.name,
        warnings=warnings,
        provenance=provenance,
    )