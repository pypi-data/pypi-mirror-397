import numpy as np

from eegcanon.features.psd import compute_psd
from eegcanon.features.bandpower import bandpower
from eegcanon.features.hjorth import hjorth_parameters


def extract_features_from_epochs(
    epochs,
    sampling_rate,
    feature_list,
):
    """
    epochs shape: (n_epochs, channels, time)
    Returns: feature matrix (n_epochs, n_features)
    """

    all_features = []

    for epoch in epochs:
        feats = []

        if "psd" in feature_list:
            feats.append(compute_psd(epoch, sampling_rate))

        if "bandpower" in feature_list:
            bp = bandpower(epoch, sampling_rate)
            feats.append(bp.flatten())

        if "hjorth" in feature_list:
            a, m, c = hjorth_parameters(epoch)
            feats.extend([a, m, c])

        feats = np.concatenate(feats)
        all_features.append(feats)

    return np.vstack(all_features)
