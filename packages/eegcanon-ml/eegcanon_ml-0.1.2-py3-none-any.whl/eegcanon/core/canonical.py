from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np

from eegcanon.core.warnings import EEGWarning


@dataclass
class CanonicalEEG:
    """
    Canonical representation of EEG data.

    Attributes
    ----------
    data : np.ndarray
        Shape (channels, time)
    channels : List[str]
        Canonical channel names
    sampling_rate : float
        Sampling frequency in Hz
    policy : str
        Channel policy applied
    warnings : List[EEGWarning]
        Structured warnings emitted during processing
    provenance : Dict[str, Any]
        Audit trail and metadata
    """

    data: np.ndarray
    channels: List[str]
    sampling_rate: float
    policy: str
    warnings: List[EEGWarning]
    provenance: Dict[str, Any]

    # -------------------------------------------------
    # Epoching API (Phase 1 - Step 1)
    # -------------------------------------------------
    def to_epochs(
        self,
        window: float,
        overlap: float = 0.0,
        drop_last: bool = True,
    ):
        from eegcanon.core.epoching import epoch_signal

        return epoch_signal(
            signal=self.data,
            sampling_rate=self.sampling_rate,
            window=window,
            overlap=overlap,
            drop_last=drop_last,
        )
    
    def extract_features(
        self,
        feature_list,
        window: float = 2.0,
        overlap: float = 0.5,
    ):
        from eegcanon.features.extract import extract_features_from_epochs

        epochs = self.to_epochs(window=window, overlap=overlap)

        features = extract_features_from_epochs(
            epochs=epochs,
            sampling_rate=self.sampling_rate,
            feature_list=feature_list,
        )

        return features
